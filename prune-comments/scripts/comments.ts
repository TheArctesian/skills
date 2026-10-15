// Run with `bun comments.ts` or `node --experimental-strip-types comments.ts` (Node >= 22.6).
// bun comments.ts inventory <files...>      -> TSV: path, comment lines, total lines
// bun comments.ts verify <rev> <files...>   -> fails when a file's comment-free code differs from <rev>
// Python is delegated to comments_py.py; every other language is compared on comment-free tokens.
import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';

// Needs a TypeScript with the JS compiler API (5.x/6.x). TypeScript 7 is a native binary without it, and Bun
// auto-install may hand back 7 for a bare `typescript`, so every candidate is checked for createSourceFile.
function loadTs() {
	const cwd = process.cwd();
	const req = createRequire(join(cwd, 'noop.js'));
	const roots = [cwd, ...readdirSync(cwd).map((d) => join(cwd, d)), dirname(new URL(import.meta.url).pathname)];
	const tried: string[] = [];
	const accept = (m: any) => {
		const mod = m?.createSourceFile ? m : m?.default;
		return mod?.createSourceFile ? mod : null;
	};
	const explicit = process.env.COMMENTS_TS_PATH;
	const names = explicit ? [explicit] : ['@typescript/typescript6', 'typescript'];
	for (const name of names) {
		try {
			const mod = accept(req(req.resolve(name, { paths: roots })));
			if (mod) return mod;
			tried.push(`${name} (no compiler API)`);
		} catch {
			tried.push(`${name} (not found)`);
		}
	}
	const store = join(cwd, 'node_modules/.bun');
	for (const hit of existsSync(store) ? readdirSync(store).filter((d) => /^(typescript|@typescript\+typescript6)@/.test(d)) : []) {
		const pkg = hit.startsWith('typescript@') ? 'typescript' : '@typescript/typescript6';
		const mod = accept(req(join(store, hit, 'node_modules', pkg)));
		if (mod) return mod;
	}
	throw new Error(`TS/JS/Svelte files need the TypeScript compiler API (5.x or 6.x). Tried: ${tried.join(', ')}. ` +
		'Install it in the repository or point COMMENTS_TS_PATH at a typescript@5 install, e.g. ' +
		'`npm i --prefix /tmp/ts5 typescript@5 && COMMENTS_TS_PATH=/tmp/ts5/node_modules/typescript`.');
}

// Loaded on first TS/JS/Svelte file, so repositories without TypeScript can still run Python and C-family files.
let tsCache: any;
const getTs = () => (tsCache ??= loadTs());

type Lang = 'ts' | 'svelte' | 'c' | 'hash' | 'nix' | 'css' | 'py' | null;
function langOf(path: string): Lang {
	const ext = path.slice(path.lastIndexOf('.') + 1);
	if (['ts', 'tsx', 'js', 'mjs', 'cjs', 'jsx'].includes(ext)) return 'ts';
	if (ext === 'svelte') return 'svelte';
	if (['swift', 'kt', 'kts', 'rs', 'go', 'java', 'c', 'h', 'm'].includes(ext)) return 'c';
	if (['sh', 'bash', 'zsh'].includes(ext)) return 'hash';
	if (ext === 'nix') return 'nix';
	if (ext === 'css') return 'css';
	if (ext === 'py') return 'py';
	return null;
}

const squash = (s: string) => s.replace(/\s+/g, ' ').trim();

function tsTokens(text: string): string {
	const ts = getTs();
	const sf = ts.createSourceFile('x.ts', text, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
	const out: string[] = [];
	const walk = (n: any) => {
		if (n.kind >= ts.SyntaxKind.FirstJSDocNode && n.kind <= ts.SyntaxKind.LastJSDocNode) return;
		const kids = n.getChildren(sf);
		if (kids.length === 0) out.push(`${n.kind}:${n.getText(sf)}`);
		else kids.forEach(walk);
	};
	walk(sf);
	return out.join('\u0001');
}

function tsCommentLines(text: string): number {
	const ts = getTs();
	let n = 0;
	const sf = ts.createSourceFile('x.ts', text, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
	const seen = new Set<number>();
	const visit = (node: any) => {
		for (const r of [...(ts.getLeadingCommentRanges(text, node.getFullStart()) ?? []), ...(ts.getTrailingCommentRanges(text, node.getEnd()) ?? [])]) {
			if (seen.has(r.pos)) continue;
			seen.add(r.pos);
			n += text.slice(r.pos, r.end).split('\n').length;
		}
		node.getChildren(sf).forEach(visit);
	};
	visit(sf);
	return n;
}

// C-family lexer: //, nestable /* */, "", """ """, Swift #""#, Rust r#""#, Go ``, char literals.
function lexC(text: string, path: string): { code: string; comments: number } {
	const nest = /\.(swift|rs|kt|kts)$/.test(path);
	const rust = path.endsWith('.rs');
	let code = '';
	let comments = 0;
	let i = 0;
	const n = text.length;
	while (i < n) {
		const c = text[i];
		const two = text.slice(i, i + 2);
		if (two === '//') {
			const j = text.indexOf('\n', i);
			comments++;
			code += ' ';
			i = j < 0 ? n : j;
		} else if (two === '/*') {
			let depth = 1;
			let j = i + 2;
			while (j < n && depth > 0) {
				if (nest && text.startsWith('/*', j)) { depth++; j += 2; }
				else if (text.startsWith('*/', j)) { depth--; j += 2; }
				else j++;
			}
			comments += text.slice(i, j).split('\n').length;
			code += ' ';
			i = j;
		} else if (c === '"' || c === '#' || (rust && (c === 'r' || c === 'b') && /^b?r#*"/.test(text.slice(i, i + 8)) && !/[A-Za-z0-9_]/.test(text[i - 1] ?? ''))) {
			const m = /^(b?r)?(#*)("""|")/.exec(text.slice(i, i + 300));
			if (!m || (c === '#' && !m[2])) { code += c; i++; continue; }
			const raw = !!m[1] || m[2].length > 0;
			const close = m[3] + m[2];
			let j = i + m[0].length;
			while (j < n && !text.startsWith(close, j)) j += !raw && text[j] === '\\' ? 2 : 1;
			j += close.length;
			code += text.slice(i, j);
			i = j;
		} else if (c === '`' && path.endsWith('.go')) {
			const j = text.indexOf('`', i + 1);
			const end = j < 0 ? n : j + 1;
			code += text.slice(i, end);
			i = end;
		} else if (c === "'") {
			const m = /^'(\\(u\{[0-9a-fA-F]+\}|.)[^']{0,8}|[^\\'\n]{1,2})'/.exec(text.slice(i, i + 16));
			const end = m ? i + m[0].length : i + 1;
			code += text.slice(i, end);
			i = end;
		} else {
			code += c;
			i++;
		}
	}
	return { code, comments };
}

// # comments outside quotes and heredocs; a # that ends a word or follows $ is code.
function lexHash(text: string, nix: boolean): { code: string; comments: number } {
	let code = '';
	let comments = 0;
	let i = 0;
	const n = text.length;
	let heredoc: string | null = null;
	while (i < n) {
		if (heredoc) {
			const j = text.indexOf('\n', i);
			const line = text.slice(i, j < 0 ? n : j);
			code += line + '\n';
			if (line.trim() === heredoc) heredoc = null;
			i = j < 0 ? n : j + 1;
			continue;
		}
		const c = text[i];
		const prev = text[i - 1] ?? '\n';
		if (nix && text.startsWith('/*', i)) {
			const j = text.indexOf('*/', i + 2);
			const end = j < 0 ? n : j + 2;
			comments += text.slice(i, end).split('\n').length;
			code += ' ';
			i = end;
		} else if (c === '#' && /\s/.test(prev) && !(i === 0 && text[1] === '!')) {
			const j = text.indexOf('\n', i);
			comments++;
			code += ' ';
			i = j < 0 ? n : j;
		} else if (c === "'" && nix && text[i + 1] === "'") {
			const j = text.indexOf("''", i + 2);
			const end = j < 0 ? n : j + 2;
			code += text.slice(i, end);
			i = end;
		} else if (c === "'" && !nix) {
			const j = text.indexOf("'", i + 1);
			const end = j < 0 ? n : j + 1;
			code += text.slice(i, end);
			i = end;
		} else if (c === '"') {
			let j = i + 1;
			while (j < n && text[j] !== '"') j += text[j] === '\\' ? 2 : 1;
			code += text.slice(i, j + 1);
			i = j + 1;
		} else if (!nix && text.startsWith('<<', i)) {
			const m = /^<<-?\s*['"]?([A-Za-z_][A-Za-z0-9_]*)['"]?/.exec(text.slice(i, i + 80));
			if (m) {
				heredoc = m[1];
				const j = text.indexOf('\n', i);
				code += text.slice(i, j < 0 ? n : j + 1);
				i = j < 0 ? n : j + 1;
			} else { code += c; i++; }
		} else {
			code += c;
			i++;
		}
	}
	return { code, comments };
}

function svelteParts(text: string) {
	const out: { kind: 'script' | 'style' | 'markup'; text: string }[] = [];
	let last = 0;
	for (const m of text.matchAll(/<(script|style)\b[^>]*>([\s\S]*?)<\/\1>/g)) {
		out.push({ kind: 'markup', text: text.slice(last, m.index) });
		out.push({ kind: m[1] as 'script' | 'style', text: m[2] });
		last = m.index! + m[0].length;
	}
	out.push({ kind: 'markup', text: text.slice(last) });
	return out;
}

function strip(path: string, text: string): string {
	switch (langOf(path)) {
		case 'ts': return tsTokens(text);
		case 'svelte':
			return svelteParts(text).map((p) =>
				p.kind === 'script' ? tsTokens(p.text)
				: p.kind === 'style' ? squash(p.text.replace(/\/\*[\s\S]*?\*\//g, ' '))
				: squash(p.text.replace(/<!--[\s\S]*?-->/g, ' '))).join('\n§\n');
		case 'c': return squash(lexC(text, path).code);
		case 'hash': return squash(lexHash(text, false).code);
		case 'nix': return squash(lexHash(text, true).code);
		case 'css': return squash(text.replace(/\/\*[\s\S]*?\*\//g, ' '));
		default: return text;
	}
}

function commentLines(path: string, text: string): number {
	switch (langOf(path)) {
		case 'ts': return tsCommentLines(text);
		case 'svelte':
			return svelteParts(text).reduce((sum, p) =>
				sum + (p.kind === 'script' ? tsCommentLines(p.text)
				: [...p.text.matchAll(p.kind === 'style' ? /\/\*[\s\S]*?\*\//g : /<!--[\s\S]*?-->/g)].reduce((s, m) => s + m[0].split('\n').length, 0)), 0);
		case 'c': return lexC(text, path).comments;
		case 'hash': return lexHash(text, false).comments;
		case 'nix': return lexHash(text, true).comments;
		case 'css': return [...text.matchAll(/\/\*[\s\S]*?\*\//g)].reduce((s, m) => s + m[0].split('\n').length, 0);
		default: return 0;
	}
}

const pyHelper = join(dirname(new URL(import.meta.url).pathname), 'comments_py.py');
const [mode, ...rest] = process.argv.slice(2);
const files = (list: string[]) => list.filter((f) => langOf(f));
if (mode === 'inventory') {
	const py = files(rest).filter((f) => f.endsWith('.py'));
	if (py.length) process.stdout.write(execFileSync('python3', ['-I', pyHelper, 'inventory', ...py], { encoding: 'utf8', maxBuffer: 1 << 28 }));
	for (const f of files(rest).filter((f) => !f.endsWith('.py'))) {
		const t = readFileSync(f, 'utf8');
		console.log(`${f}\t${commentLines(f, t)}\t${t.split('\n').length}`);
	}
} else if (mode === 'verify') {
	const [rev, ...list] = rest;
	let bad = 0;
	const py = files(list).filter((f) => f.endsWith('.py'));
	if (py.length) {
		try { execFileSync('python3', ['-I', pyHelper, 'verify', rev, ...py], { stdio: 'inherit' }); }
		catch { bad++; }
	}
	const others = files(list).filter((f) => !f.endsWith('.py'));
	for (const f of others) {
		let before = '';
		try { before = execFileSync('git', ['show', `${rev}:${f}`], { encoding: 'utf8', maxBuffer: 1 << 28, stdio: ['ignore', 'pipe', 'ignore'] }); }
		catch { console.log(`NEW FILE (not a comment edit): ${f}`); bad++; continue; }
		const after = existsSync(f) ? readFileSync(f, 'utf8') : '';
		if (strip(f, before) !== strip(f, after)) { console.log(`CODE CHANGED: ${f}`); bad++; }
	}
	console.log(`verified ${py.length + others.length} files${bad ? ', FAILURES above' : ', 0 with code changes'}`);
	process.exit(bad ? 1 : 0);
} else {
	console.error('usage: comments.ts inventory <files...> | verify <rev> <files...>');
	process.exit(2);
}
