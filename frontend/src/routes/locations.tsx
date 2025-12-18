import { useState, useMemo, useRef, useEffect } from 'react'
import { useSearchParams, useRevalidator, Link } from 'react-router'
import type { Route } from "./+types/locations"
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { locationsApi } from '@/services/api'
import type { Location } from '@/types'
import { MapPin, Search, Trash2, ChevronLeft, ChevronRight, Calendar, Skull, X } from 'lucide-react'
import 'leaflet/dist/leaflet.css'
import type { Map as LeafletMap, CircleMarker as LeafletCircleMarker } from 'leaflet'

// Country coordinates for African countries
const countryCoords: Record<string, [number, number]> = {
  'Nigeria': [9.0820, 8.6753],
  'Somalia': [5.1521, 46.1996],
  'Sudan': [12.8628, 30.2176],
  'DRC': [-4.0383, 21.7587],
  'Congo': [-0.2280, 15.8277],
  'Ethiopia': [9.1450, 40.4897],
  'Kenya': [-0.0236, 37.9062],
  'Mali': [17.5707, -3.9962],
  'Burkina Faso': [12.2383, -1.5616],
  'Cameroon': [7.3697, 12.3547],
  'Central African Republic': [6.6111, 20.9394],
  'South Sudan': [6.8770, 31.3070],
  'Libya': [26.3351, 17.2283],
  'Mozambique': [-18.6657, 35.5296],
  'Niger': [17.6078, 8.0817],
  'Uganda': [1.3733, 32.2903],
  'Chad': [15.4542, 18.7322],
  'Unknown': [5, 20],
}

const cityCoords: Record<string, [number, number]> = {
  'Maiduguri': [11.8333, 13.1500],
  'Mogadishu': [2.0469, 45.3182],
  'Khartoum': [15.5007, 32.5599],
  'Beni': [0.4997, 29.4732],
  'Juba': [4.8594, 31.5713],
  'Bamako': [12.6392, -8.0029],
  'Nairobi': [-1.2921, 36.8219],
  'Addis Ababa': [9.0320, 38.7469],
  'Ouagadougou': [12.3714, -1.5197],
  'Yaoundé': [3.8480, 11.5021],
  'Tripoli': [32.8872, 13.1913],
  'Maputo': [-25.9692, 32.5732],
  'Bria': [6.5364, 21.9876],
  'Bambari': [5.7667, 20.6667],
  'Goma': [-1.6792, 29.2228],
  'Lagos': [6.5244, 3.3792],
  'Abuja': [9.0765, 7.3986],
  'Niamey': [13.5127, 2.1128],
  'Mombasa': [-4.0435, 39.6682],
  'Kismayo': [-0.3582, 42.5454],
  'Darfur': [13.5, 25.0],
}

interface LocationEvent {
  event_id: string
  event_description: string
  date_normalized: string | null
  deaths: number
  injuries: number
  actor_normalized: string | null
  severity: string | null
}

const LIMIT = 20

function getLocationCoords(loc: Location): [number, number] | null {
  if (loc.city && cityCoords[loc.city]) return cityCoords[loc.city]
  if (countryCoords[loc.country]) return countryCoords[loc.country]
  return null
}

// React Router 7 clientLoader - fetches paginated and all locations
export async function clientLoader({ request }: Route.LoaderArgs) {
  const url = new URL(request.url)
  const page = parseInt(url.searchParams.get('page') || '1')
  const country = url.searchParams.get('country') || ''

  const [locations, allLocations] = await Promise.all([
    locationsApi.list({
      limit: LIMIT,
      offset: (page - 1) * LIMIT,
      country: country || undefined,
    }),
    locationsApi.list({ limit: 200 }),
  ])

  return {
    locations: locations as Location[],
    allLocations: allLocations as Location[],
    page,
    country
  }
}

function getMarkerColor(deaths: number): string {
  if (deaths > 50) return '#ef4444'
  if (deaths > 20) return '#f97316'
  if (deaths > 5) return '#eab308'
  return '#3b82f6'
}

// Component to handle map interactions
function MapController({
  selectedLocation,
  onPopupClose,
  markerRefs
}: {
  selectedLocation: Location | null
  onPopupClose: () => void
  markerRefs: React.MutableRefObject<Map<number, LeafletCircleMarker>>
}) {
  const map = useMap()

  useEffect(() => {
    if (selectedLocation) {
      const coords = getLocationCoords(selectedLocation)
      if (coords) {
        // Gentle zoom to level 5, then open popup
        map.flyTo(coords, 5, { duration: 0.8 })

        // Open the popup after the fly animation
        setTimeout(() => {
          const marker = markerRefs.current.get(selectedLocation.location_id)
          if (marker) {
            marker.openPopup()
          }
        }, 850)
      }
    }
  }, [selectedLocation, map, markerRefs])

  useEffect(() => {
    map.on('popupclose', onPopupClose)
    return () => {
      map.off('popupclose', onPopupClose)
    }
  }, [map, onPopupClose])

  return null
}

export default function Locations({ loaderData }: Route.ComponentProps) {
  const { locations, allLocations, page, country: initialCountry } = loaderData
  const [searchParams, setSearchParams] = useSearchParams()
  const revalidator = useRevalidator()
  const [countryFilter, setCountryFilter] = useState(initialCountry)
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null)
  const [locationEvents, setLocationEvents] = useState<LocationEvent[]>([])
  const [eventsLoading, setEventsLoading] = useState(false)
  const mapRef = useRef<LeafletMap | null>(null)
  const markerRefs = useRef<Map<number, LeafletCircleMarker>>(new Map())

  const isLoading = revalidator.state === 'loading'

  const setPage = (newPage: number) => {
    const params = new URLSearchParams(searchParams)
    params.set('page', String(newPage))
    setSearchParams(params)
  }

  const handleSearch = () => {
    const params = new URLSearchParams(searchParams)
    params.set('page', '1')
    if (countryFilter) {
      params.set('country', countryFilter)
    } else {
      params.delete('country')
    }
    setSearchParams(params)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this location?')) return
    try {
      await locationsApi.delete(id)
      revalidator.revalidate()
    } catch (e) {
      console.error('Failed to delete location:', e)
    }
  }

  const handleLocationSelect = async (location: Location) => {
    setSelectedLocation(location)
    setEventsLoading(true)
    try {
      const events = await locationsApi.getEvents(location.location_id, 20)
      setLocationEvents(events as LocationEvent[])
    } catch (e) {
      console.error('Failed to load location events:', e)
      setLocationEvents([])
    } finally {
      setEventsLoading(false)
    }
  }

  const handlePopupClose = () => {
    setSelectedLocation(null)
    setLocationEvents([])
  }

  const locationsWithCoords = useMemo(() =>
    allLocations.filter(loc => getLocationCoords(loc) !== null),
    [allLocations]
  )

  const stats = useMemo(() => ({
    totalLocations: locationsWithCoords.length,
    totalEvents: locationsWithCoords.reduce((sum, l) => sum + l.event_count, 0),
    totalDeaths: locationsWithCoords.reduce((sum, l) => sum + l.total_deaths, 0),
  }), [locationsWithCoords])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Locations</h1>
          <p className="text-muted-foreground">
            Countries, cities, and regions with event mapping
          </p>
        </div>
        <div className="flex gap-4 text-sm">
          <span>{stats.totalLocations} locations</span>
          <span>{stats.totalEvents} events</span>
          <span className="text-red-500">{stats.totalDeaths} deaths</span>
        </div>
      </div>

      {/* Map */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Event Map
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <MapContainer
              center={[5, 20]}
              zoom={3}
              style={{ height: '400px', width: '100%', borderRadius: '0.5rem' }}
              scrollWheelZoom={true}
              ref={mapRef}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <MapController
                selectedLocation={selectedLocation}
                onPopupClose={handlePopupClose}
                markerRefs={markerRefs}
              />

              {locationsWithCoords.map((loc) => {
                const coords = getLocationCoords(loc)
                if (!coords) return null

                const radius = Math.min(6 + loc.event_count * 2, 25)
                const color = getMarkerColor(loc.total_deaths)
                const isSelected = selectedLocation?.location_id === loc.location_id

                return (
                  <CircleMarker
                    key={loc.location_id}
                    center={coords}
                    radius={isSelected ? radius + 4 : radius}
                    pathOptions={{
                      fillColor: color,
                      color: isSelected ? '#000' : '#fff',
                      weight: isSelected ? 3 : 2,
                      opacity: 1,
                      fillOpacity: 0.8,
                    }}
                    eventHandlers={{
                      click: () => handleLocationSelect(loc),
                    }}
                    ref={(ref) => {
                      if (ref) {
                        markerRefs.current.set(loc.location_id, ref)
                      }
                    }}
                  >
                    <Popup>
                      <div className="min-w-[180px]">
                        <h4 className="font-semibold text-sm mb-1">
                          {loc.city || loc.country}
                        </h4>
                        {loc.city && (
                          <p className="text-xs text-gray-500 mb-2">{loc.country}</p>
                        )}
                        <div className="grid grid-cols-2 gap-2">
                          <div className="bg-blue-50 p-2 rounded text-center">
                            <p className="text-lg font-bold text-blue-600">{loc.event_count}</p>
                            <p className="text-[10px] text-gray-500">Events</p>
                          </div>
                          <div className="bg-red-50 p-2 rounded text-center">
                            <p className="text-lg font-bold text-red-600">{loc.total_deaths}</p>
                            <p className="text-[10px] text-gray-500">Deaths</p>
                          </div>
                        </div>
                      </div>
                    </Popup>
                  </CircleMarker>
                )
              })}
            </MapContainer>

            {/* Legend */}
            <div className="absolute bottom-4 left-4 bg-white/95 dark:bg-gray-800/95 rounded-lg shadow-lg p-3 z-[1000]">
              <p className="text-xs font-semibold mb-2">Deaths</p>
              <div className="space-y-1 text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-red-500" />
                  <span>&gt; 50</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-orange-500" />
                  <span>21-50</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-yellow-500" />
                  <span>6-20</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-blue-500" />
                  <span>0-5</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Events for Selected Location */}
      {selectedLocation && (
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Events in {selectedLocation.city || selectedLocation.country}
                <span className="text-sm font-normal text-muted-foreground">
                  ({selectedLocation.event_count} events)
                </span>
              </CardTitle>
              <Button variant="ghost" size="icon" onClick={handlePopupClose}>
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {eventsLoading ? (
              <div className="flex justify-center py-8">
                <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
              </div>
            ) : locationEvents.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">No events found</p>
            ) : (
              <div className="divide-y max-h-[300px] overflow-y-auto">
                {locationEvents.map((event) => (
                  <div key={event.event_id} className="py-3 first:pt-0 last:pb-0">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          {event.severity && (
                            <span className={`text-xs px-2 py-0.5 rounded ${
                              event.severity === 'Critical' ? 'bg-red-100 text-red-700' :
                              event.severity === 'High' ? 'bg-orange-100 text-orange-700' :
                              event.severity === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-gray-100 text-gray-700'
                            }`}>
                              {event.severity}
                            </span>
                          )}
                          <span className="text-xs text-muted-foreground">
                            {event.date_normalized || 'Unknown date'}
                          </span>
                        </div>
                        <p className="text-sm line-clamp-2">{event.event_description}</p>
                        <div className="flex items-center gap-4 mt-1 text-xs text-muted-foreground">
                          {event.actor_normalized && (
                            <span>Actor: {event.actor_normalized}</span>
                          )}
                          <span className="flex items-center gap-1 text-red-500">
                            <Skull className="h-3 w-3" />
                            {event.deaths}
                          </span>
                          {event.injuries > 0 && (
                            <span className="text-orange-500">{event.injuries} injured</span>
                          )}
                        </div>
                      </div>
                      <Button variant="ghost" size="sm" asChild>
                        <Link to={`/events/${event.event_id}`}>View</Link>
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Filter by country..."
                value={countryFilter}
                onChange={(e) => setCountryFilter(e.target.value)}
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

      {/* Locations List */}
      <Card>
        <CardHeader>
          <CardTitle>All Locations</CardTitle>
        </CardHeader>
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
                <div
                  key={location.location_id}
                  className={`flex items-center gap-4 p-4 hover:bg-muted/50 cursor-pointer ${
                    selectedLocation?.location_id === location.location_id ? 'bg-primary/10' : ''
                  }`}
                  onClick={() => handleLocationSelect(location)}
                >
                  <MapPin className="h-5 w-5 text-muted-foreground" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium">{location.country}</span>
                      {location.city && (
                        <span className="text-muted-foreground">- {location.city}</span>
                      )}
                      {location.location_type && (
                        <span className="rounded bg-primary/10 px-2 py-0.5 text-xs">
                          {location.location_type}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      {location.region && <span>Region: {location.region}</span>}
                      <span>{location.event_count} events</span>
                      <span className="text-red-500">{location.total_deaths} deaths</span>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDelete(location.location_id)
                    }}
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

      {/* Pagination */}
      <div className="flex items-center justify-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setPage(Math.max(1, page - 1))}
          disabled={page === 1}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <span className="text-sm text-muted-foreground">Page {page}</span>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setPage(page + 1)}
          disabled={locations.length < LIMIT}
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
