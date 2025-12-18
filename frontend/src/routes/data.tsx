import { useState } from 'react'
import { Link, useSearchParams, useRevalidator } from 'react-router'
import type { Route } from "./+types/data"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { eventsApi, actorsApi, locationsApi, taxonomiesApi, analyticsApi } from '@/services/api'
import type { Event, Actor, Location, Taxonomy } from '@/types'
import {
  Calendar,
  ChevronLeft,
  ChevronRight,
  Eye,
  Trash2,
  Flag,
  Users,
  MapPin,
  Tags,
  Database,
  Search
} from 'lucide-react'

const LIMIT = 15

export async function clientLoader({ request }: Route.LoaderArgs) {
  const url = new URL(request.url)
  const tab = url.searchParams.get('tab') || 'events'
  const page = parseInt(url.searchParams.get('page') || '1')
  const search = url.searchParams.get('search') || ''
  const country = url.searchParams.get('country') || ''
  const severity = url.searchParams.get('severity') || ''
  const flagged = url.searchParams.get('flagged') === 'true'

  // Fetch stats for all tabs
  const stats = await analyticsApi.getStats().catch(() => null)

  // Fetch data based on active tab
  let events: Event[] = []
  let actors: Actor[] = []
  let locations: Location[] = []
  let taxonomies: Taxonomy[] = []
  let total = 0

  const offset = (page - 1) * LIMIT

  switch (tab) {
    case 'events':
      const eventsData = await eventsApi.list({
        limit: LIMIT,
        offset,
        country: country || undefined,
        actor: search || undefined,
        severity: severity || undefined,
        flagged: flagged || undefined,
      })
      events = eventsData.events as Event[]
      total = eventsData.total
      break

    case 'actors':
      actors = await actorsApi.list({
        limit: LIMIT,
        offset,
        search: search || undefined,
      }) as Actor[]
      total = stats?.total_actors || actors.length
      break

    case 'locations':
      locations = await locationsApi.list({
        limit: LIMIT,
        offset,
        search: search || undefined,
      }) as Location[]
      total = stats?.total_locations || locations.length
      break

    case 'taxonomies':
      taxonomies = await taxonomiesApi.list({
        limit: LIMIT,
        offset,
        search: search || undefined,
      }) as Taxonomy[]
      total = stats?.total_taxonomies || taxonomies.length
      break
  }

  return {
    tab,
    page,
    search,
    country,
    severity,
    flagged,
    stats,
    events,
    actors,
    locations,
    taxonomies,
    total
  }
}

export default function DataExplorer({ loaderData }: Route.ComponentProps) {
  const {
    tab,
    page,
    search: initialSearch,
    country,
    severity,
    flagged,
    stats,
    events,
    actors,
    locations,
    taxonomies,
    total
  } = loaderData

  const [searchParams, setSearchParams] = useSearchParams()
  const revalidator = useRevalidator()
  const [search, setSearch] = useState(initialSearch)

  const totalPages = Math.ceil(total / LIMIT)
  const isLoading = revalidator.state === 'loading'

  const updateParams = (updates: Record<string, string>) => {
    const params = new URLSearchParams(searchParams)
    Object.entries(updates).forEach(([key, value]) => {
      if (value) {
        params.set(key, value)
      } else {
        params.delete(key)
      }
    })
    setSearchParams(params)
  }

  const setTab = (newTab: string) => {
    setSearch('')
    updateParams({ tab: newTab, page: '1', search: '', country: '', severity: '' })
  }

  const setPage = (newPage: number) => {
    updateParams({ page: String(newPage) })
  }

  const handleSearch = () => {
    updateParams({ search, page: '1' })
  }

  const handleDelete = async (type: string, id: string | number) => {
    if (!confirm(`Delete this ${type}?`)) return
    try {
      switch (type) {
        case 'event':
          await eventsApi.delete(id as string)
          break
        case 'actor':
          await actorsApi.delete(id as number)
          break
        case 'location':
          await locationsApi.delete(id as number)
          break
      }
      revalidator.revalidate()
    } catch (e) {
      console.error(`Failed to delete ${type}:`, e)
    }
  }

  const handleToggleFlag = async (id: string, currentlyFlagged: boolean) => {
    try {
      if (currentlyFlagged) {
        await eventsApi.unflag(id)
      } else {
        await eventsApi.flag(id, 'Flagged for review')
      }
      revalidator.revalidate()
    } catch (e) {
      console.error('Failed to toggle flag:', e)
    }
  }

  const getSeverityColor = (sev: string | null) => {
    switch (sev) {
      case 'Critical': return 'bg-red-500/10 text-red-500'
      case 'High': return 'bg-orange-500/10 text-orange-500'
      case 'Medium': return 'bg-yellow-500/10 text-yellow-500'
      case 'Low': return 'bg-green-500/10 text-green-500'
      default: return 'bg-gray-500/10 text-gray-500'
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Events</h1>
        <p className="text-muted-foreground">
          Browse and manage events, actors, locations, and taxonomies
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className={tab === 'events' ? 'border-primary' : ''}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Events</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_events?.toLocaleString() || '-'}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.countries_covered || 0} countries
            </p>
          </CardContent>
        </Card>

        <Card className={tab === 'actors' ? 'border-primary' : ''}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Actors</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_actors?.toLocaleString() || '-'}</div>
            <p className="text-xs text-muted-foreground">Armed groups</p>
          </CardContent>
        </Card>

        <Card className={tab === 'locations' ? 'border-primary' : ''}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Locations</CardTitle>
            <MapPin className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_locations?.toLocaleString() || '-'}</div>
            <p className="text-xs text-muted-foreground">Cities & regions</p>
          </CardContent>
        </Card>

        <Card className={tab === 'taxonomies' ? 'border-primary' : ''}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Taxonomies</CardTitle>
            <Tags className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_taxonomies?.toLocaleString() || '-'}</div>
            <p className="text-xs text-muted-foreground">Classifications</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={tab} onValueChange={setTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="events" className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            Events
          </TabsTrigger>
          <TabsTrigger value="actors" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            Actors
          </TabsTrigger>
          <TabsTrigger value="locations" className="flex items-center gap-2">
            <MapPin className="h-4 w-4" />
            Locations
          </TabsTrigger>
          <TabsTrigger value="taxonomies" className="flex items-center gap-2">
            <Tags className="h-4 w-4" />
            Taxonomies
          </TabsTrigger>
        </TabsList>

        {/* Events Tab */}
        <TabsContent value="events" className="space-y-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-wrap gap-4">
                <div className="flex-1 min-w-[200px]">
                  <Input
                    placeholder="Filter by country..."
                    value={country}
                    onChange={(e) => updateParams({ country: e.target.value, page: '1' })}
                  />
                </div>
                <div className="flex-1 min-w-[200px]">
                  <Input
                    placeholder="Filter by actor..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  />
                </div>
                <div className="w-[150px]">
                  <Select
                    value={severity || 'all'}
                    onValueChange={(v) => updateParams({ severity: v === 'all' ? '' : v, page: '1' })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Severity" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Severities</SelectItem>
                      <SelectItem value="Critical">Critical</SelectItem>
                      <SelectItem value="High">High</SelectItem>
                      <SelectItem value="Medium">Medium</SelectItem>
                      <SelectItem value="Low">Low</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button
                  variant={flagged ? 'default' : 'outline'}
                  onClick={() => updateParams({ flagged: flagged ? '' : 'true', page: '1' })}
                >
                  <Flag className="mr-2 h-4 w-4" />
                  Flagged
                </Button>
                <Button variant="outline" onClick={() => updateParams({ country: '', search: '', severity: '', flagged: '', page: '1' })}>
                  Clear
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-0">
              {isLoading ? (
                <div className="flex justify-center py-12">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                </div>
              ) : events.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                  <Calendar className="h-12 w-12 mb-4" />
                  <p>No events found</p>
                </div>
              ) : (
                <div className="divide-y">
                  {events.map((event) => (
                    <div key={event.event_id} className={`flex items-center gap-4 p-4 hover:bg-muted/50 ${event.flagged_for_review ? 'bg-orange-500/5 border-l-2 border-l-orange-500' : ''}`}>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          {event.flagged_for_review && (
                            <span className="rounded px-2 py-0.5 text-xs bg-orange-500/10 text-orange-500">
                              Flagged
                            </span>
                          )}
                          <span className={`rounded px-2 py-0.5 text-xs ${getSeverityColor(event.severity)}`}>
                            {event.severity || 'Unknown'}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {event.date_normalized || 'No date'}
                          </span>
                        </div>
                        <p className="font-medium truncate">{event.event_description}</p>
                        <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                          <span>{event.location_country}{event.location_city ? `, ${event.location_city}` : ''}</span>
                          {event.actor_normalized && <span>Actor: {event.actor_normalized}</span>}
                          <span className="text-red-500">{event.deaths} deaths</span>
                          <span className="text-orange-500">{event.injuries} injuries</span>
                        </div>
                      </div>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="icon" asChild>
                          <Link to={`/events/${event.event_id}`}>
                            <Eye className="h-4 w-4" />
                          </Link>
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleToggleFlag(event.event_id, event.flagged_for_review || false)}
                          title={event.flagged_for_review ? 'Remove flag' : 'Flag for review'}
                        >
                          <Flag className={`h-4 w-4 ${event.flagged_for_review ? 'fill-orange-500 text-orange-500' : ''}`} />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => handleDelete('event', event.event_id)}>
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Actors Tab */}
        <TabsContent value="actors" className="space-y-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex gap-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search actors..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  />
                </div>
                <Button onClick={handleSearch}>
                  <Search className="mr-2 h-4 w-4" />
                  Search
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-0">
              {isLoading ? (
                <div className="flex justify-center py-12">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                </div>
              ) : actors.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                  <Users className="h-12 w-12 mb-4" />
                  <p>No actors found</p>
                </div>
              ) : (
                <div className="divide-y">
                  {actors.map((actor) => (
                    <div key={actor.actor_id} className="flex items-center gap-4 p-4 hover:bg-muted/50">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium">{actor.actor_name}</span>
                          {actor.actor_type && (
                            <span className="rounded bg-primary/10 px-2 py-0.5 text-xs">
                              {actor.actor_type}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          {actor.country && <span>{actor.country}</span>}
                          <span>{actor.event_count} events</span>
                          <span className="text-red-500">{actor.total_deaths} deaths</span>
                          <span className="text-orange-500">{actor.total_injuries} injuries</span>
                        </div>
                        {actor.aliases && actor.aliases.length > 0 && (
                          <div className="mt-1 text-xs text-muted-foreground">
                            Also known as: {actor.aliases.join(', ')}
                          </div>
                        )}
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete('actor', actor.actor_id)}
                        disabled={actor.event_count > 0}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Locations Tab */}
        <TabsContent value="locations" className="space-y-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex gap-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search locations..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  />
                </div>
                <Button onClick={handleSearch}>
                  <Search className="mr-2 h-4 w-4" />
                  Search
                </Button>
                <Button variant="outline" asChild>
                  <Link to="/locations">
                    <MapPin className="mr-2 h-4 w-4" />
                    View Map
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-0">
              {isLoading ? (
                <div className="flex justify-center py-12">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                </div>
              ) : locations.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                  <MapPin className="h-12 w-12 mb-4" />
                  <p>No locations found</p>
                </div>
              ) : (
                <div className="divide-y">
                  {locations.map((location) => (
                    <div key={location.location_id} className="flex items-center gap-4 p-4 hover:bg-muted/50">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium">{location.city || location.region || 'Unknown'}</span>
                          <span className="rounded bg-primary/10 px-2 py-0.5 text-xs">
                            {location.country}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          {location.region && <span>Region: {location.region}</span>}
                          <span>{location.event_count} events</span>
                          {location.latitude && location.longitude && (
                            <span>
                              {location.latitude.toFixed(2)}, {location.longitude.toFixed(2)}
                            </span>
                          )}
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete('location', location.location_id)}
                        disabled={location.event_count > 0}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Taxonomies Tab */}
        <TabsContent value="taxonomies" className="space-y-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex gap-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search taxonomies..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  />
                </div>
                <Button onClick={handleSearch}>
                  <Search className="mr-2 h-4 w-4" />
                  Search
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-0">
              {isLoading ? (
                <div className="flex justify-center py-12">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                </div>
              ) : taxonomies.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                  <Tags className="h-12 w-12 mb-4" />
                  <p>No taxonomies found</p>
                </div>
              ) : (
                <div className="divide-y">
                  {taxonomies.map((tax) => (
                    <div key={tax.taxonomy_id} className="flex items-center gap-4 p-4 hover:bg-muted/50">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium">{tax.level_1}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          {tax.level_2 && <span>{tax.level_2}</span>}
                          {tax.level_3 && <span>/ {tax.level_3}</span>}
                          {tax.level_4 && <span>/ {tax.level_4}</span>}
                        </div>
                        <div className="mt-1 text-sm text-muted-foreground">
                          {tax.event_count} events
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page === totalPages}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  )
}
