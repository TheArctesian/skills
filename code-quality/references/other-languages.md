# Other languages

When a language has no reference here, derive its idioms from the ecosystem's own
authorities before judging the I property, and record what you adopted in the audit.

| Language | Formatter / linter at defaults | Idiom sources |
|---|---|---|
| Go | `gofmt`, `go vet`, `staticcheck` or `golangci-lint` | [Effective Go](https://go.dev/doc/effective_go), [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments) |
| Swift | `swift-format`, SwiftLint | [Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/) |
| Kotlin | ktlint, detekt | [Kotlin coding conventions](https://kotlinlang.org/docs/coding-conventions.html) |
| Java | google-java-format or the repo's, Error Prone | Effective Java |
| C# | `dotnet format`, analyzers | [.NET design guidelines](https://learn.microsoft.com/dotnet/standard/design-guidelines/) |
| Ruby | RuboCop | [Ruby Style Guide](https://rubystyle.guide/) |
| Shell | `shfmt`, ShellCheck | [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html) |
| Elixir | `mix format`, Credo | [Elixir library guidelines](https://hexdocs.pm/elixir/library-guidelines.html) |

## CUPID translations that hold everywhere

- **C** Export the minimum the language allows (unexported Go identifiers, Swift
  `internal`/`private`, Kotlin `internal`). Pure core, I/O at the edge.
- **U** One package or module per concept; a file named for what it does.
- **P** Use the language's error channel (Go `error`, Swift `throws`/`Result`, Kotlin
  sealed results); never swallow it. Inject clocks and randomness.
- **I** Formatter and linter at defaults, then the neighbouring code's shape.
- **D** Packages named for domain nouns; Go in particular forbids `util`/`common`
  package names by convention, and the rule generalises.
