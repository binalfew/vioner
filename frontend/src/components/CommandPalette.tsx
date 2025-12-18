import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router'
import { Command } from 'cmdk'
import {
  LayoutDashboard,
  Brain,
  Box,
  FlaskConical,
  Database,
  MapPin,
  History,
  Settings,
  Search,
  Moon,
  Sun,
  Monitor
} from 'lucide-react'
import { useTheme } from '@/context/ThemeContext'

const pages = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard, keywords: ['home', 'overview'] },
  { name: 'Training', href: '/training', icon: Brain, keywords: ['model', 'train', 'bert', 'checkpoints'] },
  { name: 'Models', href: '/models', icon: Box, keywords: ['activate', 'trained', 'production'] },
  { name: 'Testing', href: '/testing', icon: FlaskConical, keywords: ['extract', 'ner', 'test'] },
  { name: 'History', href: '/history', icon: History, keywords: ['past', 'extractions'] },
  { name: 'Events', href: '/events', icon: Database, keywords: ['violent', 'incidents', 'data'] },
  { name: 'Locations', href: '/locations', icon: MapPin, keywords: ['cities', 'countries', 'map'] },
  { name: 'Settings', href: '/settings', icon: Settings, keywords: ['config', 'system'] },
]

export function CommandPalette() {
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()
  const { theme, setTheme } = useTheme()

  // Toggle the menu when cmd+k is pressed
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }

    document.addEventListener('keydown', down)
    return () => document.removeEventListener('keydown', down)
  }, [])

  const runCommand = useCallback((command: () => void) => {
    setOpen(false)
    command()
  }, [])

  return (
    <Command.Dialog
      open={open}
      onOpenChange={setOpen}
      label="Command Menu"
      className="fixed inset-0 z-[100]"
    >
      <div
        className="fixed inset-0 bg-black/50"
        onClick={() => setOpen(false)}
      />
      <div className="fixed left-1/2 top-1/4 -translate-x-1/2 w-full max-w-lg">
        <div className="bg-card border rounded-xl shadow-2xl overflow-hidden">
          <div className="flex items-center gap-2 px-4 border-b">
            <Search className="h-4 w-4 text-muted-foreground" />
            <Command.Input
              placeholder="Type a command or search..."
              className="flex-1 py-4 bg-transparent outline-none placeholder:text-muted-foreground"
            />
            <kbd className="hidden sm:inline-flex h-5 items-center gap-1 rounded border bg-muted px-1.5 text-[10px] font-medium text-muted-foreground">
              ESC
            </kbd>
          </div>

          <Command.List className="max-h-[300px] overflow-y-auto p-2">
            <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
              No results found.
            </Command.Empty>

            <Command.Group heading="Navigation" className="px-2 py-1.5 text-xs font-medium text-muted-foreground">
              {pages.map((page) => (
                <Command.Item
                  key={page.href}
                  value={`${page.name} ${page.keywords.join(' ')}`}
                  onSelect={() => runCommand(() => navigate(page.href))}
                  className="flex items-center gap-3 px-2 py-2 rounded-lg cursor-pointer text-sm aria-selected:bg-accent"
                >
                  <page.icon className="h-4 w-4 text-muted-foreground" />
                  {page.name}
                </Command.Item>
              ))}
            </Command.Group>

            <Command.Separator className="my-2 h-px bg-border" />

            <Command.Group heading="Theme" className="px-2 py-1.5 text-xs font-medium text-muted-foreground">
              <Command.Item
                value="light theme"
                onSelect={() => runCommand(() => setTheme('light'))}
                className="flex items-center gap-3 px-2 py-2 rounded-lg cursor-pointer text-sm aria-selected:bg-accent"
              >
                <Sun className="h-4 w-4 text-muted-foreground" />
                Light Mode
                {theme === 'light' && <span className="ml-auto text-xs text-primary">Active</span>}
              </Command.Item>
              <Command.Item
                value="dark theme"
                onSelect={() => runCommand(() => setTheme('dark'))}
                className="flex items-center gap-3 px-2 py-2 rounded-lg cursor-pointer text-sm aria-selected:bg-accent"
              >
                <Moon className="h-4 w-4 text-muted-foreground" />
                Dark Mode
                {theme === 'dark' && <span className="ml-auto text-xs text-primary">Active</span>}
              </Command.Item>
              <Command.Item
                value="system theme auto"
                onSelect={() => runCommand(() => setTheme('system'))}
                className="flex items-center gap-3 px-2 py-2 rounded-lg cursor-pointer text-sm aria-selected:bg-accent"
              >
                <Monitor className="h-4 w-4 text-muted-foreground" />
                System Theme
                {theme === 'system' && <span className="ml-auto text-xs text-primary">Active</span>}
              </Command.Item>
            </Command.Group>
          </Command.List>

          <div className="flex items-center justify-between px-4 py-2 border-t bg-muted/30 text-xs text-muted-foreground">
            <span>Navigate with arrow keys</span>
            <span>Press Enter to select</span>
          </div>
        </div>
      </div>
    </Command.Dialog>
  )
}
