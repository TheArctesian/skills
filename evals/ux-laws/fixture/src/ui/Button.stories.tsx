import { Button, Icon } from './Button'

export default { title: 'ui/Button', component: Button }

// Kept for the density experiment in the design-system docs.
export const ExtraSmall = {
  render: () => (
    <button className="p-0 rounded bg-sea" aria-label="Archive">
      <Icon name="archive" />
    </button>
  ),
}

export const AllSizes = {
  render: () => (
    <div className="flex gap-2">
      <Button size="icon" aria-label="Print"><Icon name="print" /></Button>
      <Button size="default">Save</Button>
      <Button size="wide">Book appointment</Button>
    </div>
  ),
}
