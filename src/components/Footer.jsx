// §8 Footer
export default function Footer() {
  return (
    <footer className="px-2 pt-2 sm:px-3 sm:pt-3">
      <div className="mx-auto flex max-w-[1440px] flex-col items-start justify-between gap-3 rounded-t-[2rem] bg-surface-raised px-8 py-8 sm:flex-row sm:items-center sm:px-12">
        <p className="flex items-center gap-2 text-sm text-text-faint">
          <img src="/assets/logo.svg" alt="" width="18" height="18" className="size-[18px]" />
          © 2026 Shelf. Bookmarks with a Brain. All rights reserved.
        </p>
        <p className="text-sm text-text-faint">savetoshelf.com</p>
      </div>
    </footer>
  )
}
