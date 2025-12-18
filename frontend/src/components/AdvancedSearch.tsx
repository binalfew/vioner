import { useState } from 'react'
import { useSearchParams } from 'react-router'
import { Search, Filter, X, Calendar, MapPin, Users, AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent } from '@/components/ui/card'

interface AdvancedSearchProps {
  onSearch?: (filters: SearchFilters) => void
  showCountry?: boolean
  showActor?: boolean
  showSeverity?: boolean
  showDateRange?: boolean
}

interface SearchFilters {
  search: string
  country: string
  actor: string
  severity: string
  date_from: string
  date_to: string
}

const severityOptions = [
  { value: '', label: 'All Severities' },
  { value: 'Critical', label: 'Critical' },
  { value: 'High', label: 'High' },
  { value: 'Medium', label: 'Medium' },
  { value: 'Low', label: 'Low' },
]

export function AdvancedSearch({
  onSearch,
  showCountry = true,
  showActor = true,
  showSeverity = true,
  showDateRange = true,
}: AdvancedSearchProps) {
  const [searchParams, setSearchParams] = useSearchParams()
  const [isExpanded, setIsExpanded] = useState(false)

  const [filters, setFilters] = useState<SearchFilters>({
    search: searchParams.get('search') || '',
    country: searchParams.get('country') || '',
    actor: searchParams.get('actor') || '',
    severity: searchParams.get('severity') || '',
    date_from: searchParams.get('date_from') || '',
    date_to: searchParams.get('date_to') || '',
  })

  const handleSearch = () => {
    const params = new URLSearchParams()
    params.set('page', '1')

    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        params.set(key, value)
      }
    })

    setSearchParams(params)
    onSearch?.(filters)
  }

  const handleClear = () => {
    const clearedFilters: SearchFilters = {
      search: '',
      country: '',
      actor: '',
      severity: '',
      date_from: '',
      date_to: '',
    }
    setFilters(clearedFilters)
    setSearchParams(new URLSearchParams({ page: '1' }))
    onSearch?.(clearedFilters)
  }

  const activeFilterCount = Object.values(filters).filter(Boolean).length

  return (
    <Card>
      <CardContent className="pt-6">
        {/* Basic Search */}
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search events, actors, locations..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="pl-10"
            />
          </div>
          <Button onClick={handleSearch}>
            <Search className="mr-2 h-4 w-4" />
            Search
          </Button>
          <Button
            variant="outline"
            onClick={() => setIsExpanded(!isExpanded)}
            className="relative"
          >
            <Filter className="mr-2 h-4 w-4" />
            Filters
            {activeFilterCount > 0 && (
              <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center">
                {activeFilterCount}
              </span>
            )}
          </Button>
        </div>

        {/* Advanced Filters */}
        {isExpanded && (
          <div className="mt-4 pt-4 border-t">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {showCountry && (
                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    Country
                  </Label>
                  <Input
                    placeholder="Filter by country"
                    value={filters.country}
                    onChange={(e) => setFilters({ ...filters, country: e.target.value })}
                  />
                </div>
              )}

              {showActor && (
                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <Users className="h-4 w-4" />
                    Actor
                  </Label>
                  <Input
                    placeholder="Filter by actor"
                    value={filters.actor}
                    onChange={(e) => setFilters({ ...filters, actor: e.target.value })}
                  />
                </div>
              )}

              {showSeverity && (
                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4" />
                    Severity
                  </Label>
                  <Select
                    value={filters.severity}
                    onValueChange={(value) => setFilters({ ...filters, severity: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All Severities" />
                    </SelectTrigger>
                    <SelectContent>
                      {severityOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value || 'all'}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {showDateRange && (
                <>
                  <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      From Date
                    </Label>
                    <Input
                      type="date"
                      value={filters.date_from}
                      onChange={(e) => setFilters({ ...filters, date_from: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      To Date
                    </Label>
                    <Input
                      type="date"
                      value={filters.date_to}
                      onChange={(e) => setFilters({ ...filters, date_to: e.target.value })}
                    />
                  </div>
                </>
              )}
            </div>

            <div className="flex justify-end gap-2 mt-4">
              <Button variant="ghost" onClick={handleClear}>
                <X className="mr-2 h-4 w-4" />
                Clear Filters
              </Button>
              <Button onClick={handleSearch}>
                Apply Filters
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
