export default function HeaderBar({ title }) {
  return (
    <header className="h-12 flex items-center px-4 bg-surface border-b border-zinc-700">
      <h1 className="text-base font-semibold text-zinc-100">{title}</h1>
    </header>
  )
}
