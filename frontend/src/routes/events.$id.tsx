import { useState } from 'react'
import { useNavigate, useRevalidator } from 'react-router'
import type { Route } from "./+types/events.$id"
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { eventsApi } from '@/services/api'
import type { EventDetail as EventDetailType } from '@/types'
import { ArrowLeft, Trash2, Flag, Calendar, MapPin, Users, Skull, Pencil, Loader2 } from 'lucide-react'

// React Router 7 clientLoader - fetches event by ID from params
export async function clientLoader({ params }: Route.LoaderArgs) {
  const event = await eventsApi.get(params.id!)
  return { event: event as EventDetailType }
}

export default function EventDetail({ loaderData }: Route.ComponentProps) {
  const { event } = loaderData
  const navigate = useNavigate()
  const revalidator = useRevalidator()
  const [error, setError] = useState<string | null>(null)

  // Edit modal state
  const [editOpen, setEditOpen] = useState(false)
  const [saving, setSaving] = useState(false)
  const [editForm, setEditForm] = useState({
    event_description: event.event_description,
    actor_normalized: event.actor_normalized || '',
    victim_normalized: event.victim_normalized || '',
    location_country: event.location_country,
    location_city: event.location_city || '',
    date_normalized: event.date_normalized || '',
    taxonomy_l1: event.taxonomy_l1,
    taxonomy_l2: event.taxonomy_l2 || '',
    taxonomy_l3: event.taxonomy_l3 || '',
    weapon_category: event.weapon_category || '',
    deaths: event.deaths,
    injuries: event.injuries,
  })

  // Unflag dialog state
  const [unflagOpen, setUnflagOpen] = useState(false)
  const [reviewNotes, setReviewNotes] = useState('')

  const handleDelete = async () => {
    if (!confirm('Delete this event?')) return
    try {
      await eventsApi.delete(event.event_id)
      navigate('/events')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to delete')
    }
  }

  const handleFlag = async () => {
    try {
      await eventsApi.flag(event.event_id, 'Flagged for review')
      revalidator.revalidate()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to flag')
    }
  }

  const handleUnflag = async () => {
    try {
      await eventsApi.unflag(event.event_id)
      revalidator.revalidate()
      setUnflagOpen(false)
      setReviewNotes('')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to unflag')
    }
  }

  const handleSaveEdit = async () => {
    setSaving(true)
    setError(null)
    try {
      await eventsApi.update(event.event_id, {
        event_description: editForm.event_description,
        actor_normalized: editForm.actor_normalized || undefined,
        victim_normalized: editForm.victim_normalized || undefined,
        location_country: editForm.location_country,
        location_city: editForm.location_city || undefined,
        date_normalized: editForm.date_normalized || undefined,
        taxonomy_l1: editForm.taxonomy_l1,
        taxonomy_l2: editForm.taxonomy_l2 || undefined,
        taxonomy_l3: editForm.taxonomy_l3 || undefined,
        weapon_category: editForm.weapon_category || undefined,
        deaths: editForm.deaths,
        injuries: editForm.injuries,
      })
      revalidator.revalidate()
      setEditOpen(false)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to save changes')
    } finally {
      setSaving(false)
    }
  }

  const getSeverityColor = (severity: string | null) => {
    switch (severity) {
      case 'Critical': return 'bg-red-500 text-white'
      case 'High': return 'bg-orange-500 text-white'
      case 'Medium': return 'bg-yellow-500 text-black'
      case 'Low': return 'bg-green-500 text-white'
      default: return 'bg-gray-500 text-white'
    }
  }

  return (
    <div className="space-y-6">
      {error && (
        <div className="rounded-lg bg-destructive/10 p-4 text-destructive">
          {error}
        </div>
      )}

      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={() => navigate('/events')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Events
        </Button>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setEditOpen(true)}>
            <Pencil className="mr-2 h-4 w-4" />
            Edit
          </Button>
          {event.flagged_for_review ? (
            <Button
              variant="default"
              onClick={() => setUnflagOpen(true)}
              className="bg-orange-500 hover:bg-orange-600"
            >
              <Flag className="mr-2 h-4 w-4 fill-current" />
              Mark Reviewed
            </Button>
          ) : (
            <Button variant="outline" onClick={handleFlag}>
              <Flag className="mr-2 h-4 w-4" />
              Flag
            </Button>
          )}
          <Button variant="destructive" onClick={handleDelete}>
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </Button>
        </div>
      </div>

      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          {event.flagged_for_review && (
            <span className="rounded px-2 py-1 text-sm bg-orange-500 text-white flex items-center gap-1">
              <Flag className="h-3 w-3 fill-current" />
              Flagged
            </span>
          )}
          <span className={`rounded px-2 py-1 text-sm ${getSeverityColor(event.severity)}`}>
            {event.severity || 'Unknown'}
          </span>
          <span className="text-sm text-muted-foreground">{event.taxonomy_l1}</span>
          {event.taxonomy_l2 && (
            <span className="text-sm text-muted-foreground">/ {event.taxonomy_l2}</span>
          )}
        </div>
        <h1 className="text-2xl font-bold">{event.event_description}</h1>
        {event.flagged_for_review && event.review_notes && (
          <div className="rounded-lg bg-orange-500/10 border border-orange-500/20 p-3 text-sm">
            <span className="font-medium text-orange-600">Review Notes:</span> {event.review_notes}
          </div>
        )}
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="flex items-center gap-3 pt-6">
            <Calendar className="h-8 w-8 text-muted-foreground" />
            <div>
              <p className="text-sm text-muted-foreground">Date</p>
              <p className="font-medium">{event.date_normalized || 'Unknown'}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 pt-6">
            <MapPin className="h-8 w-8 text-muted-foreground" />
            <div>
              <p className="text-sm text-muted-foreground">Location</p>
              <p className="font-medium">
                {event.location_country}
                {event.location_city && `, ${event.location_city}`}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 pt-6">
            <Users className="h-8 w-8 text-muted-foreground" />
            <div>
              <p className="text-sm text-muted-foreground">Actor</p>
              <p className="font-medium">{event.actor_normalized || 'Unknown'}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 pt-6">
            <Skull className="h-8 w-8 text-red-500" />
            <div>
              <p className="text-sm text-muted-foreground">Casualties</p>
              <p className="font-medium">
                {event.deaths} deaths, {event.injuries} injuries
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Details */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* WHO */}
        <Card>
          <CardHeader>
            <CardTitle>WHO - Actors</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground">Perpetrator</p>
              <p className="font-medium">{event.actor_normalized || '-'}</p>
              {event.actor_type && (
                <p className="text-sm text-muted-foreground">Type: {event.actor_type}</p>
              )}
              {event.actor_confidence && (
                <p className="text-xs text-muted-foreground">
                  Confidence: {(event.actor_confidence * 100).toFixed(1)}%
                </p>
              )}
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Victim</p>
              <p className="font-medium">{event.victim_normalized || '-'}</p>
              {event.victim_type && (
                <p className="text-sm text-muted-foreground">Type: {event.victim_type}</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* WHERE */}
        <Card>
          <CardHeader>
            <CardTitle>WHERE - Location</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Country</p>
                <p className="font-medium">{event.location_country}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">City</p>
                <p className="font-medium">{event.location_city || '-'}</p>
              </div>
            </div>
            {event.location_confidence && (
              <p className="text-xs text-muted-foreground">
                Confidence: {(event.location_confidence * 100).toFixed(1)}%
              </p>
            )}
          </CardContent>
        </Card>

        {/* WHEN */}
        <Card>
          <CardHeader>
            <CardTitle>WHEN - Time</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Normalized Date</p>
                <p className="font-medium">{event.date_normalized || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Original Text</p>
                <p className="font-medium">{event.date_original || '-'}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* WHAT */}
        <Card>
          <CardHeader>
            <CardTitle>WHAT - Event Type</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Level 1</p>
                <p className="font-medium">{event.taxonomy_l1}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Level 2</p>
                <p className="font-medium">{event.taxonomy_l2 || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Level 3</p>
                <p className="font-medium">{event.taxonomy_l3 || '-'}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* HOW */}
        <Card>
          <CardHeader>
            <CardTitle>HOW - Method & Casualties</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Weapon</p>
                <p className="font-medium">{event.weapon_category || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Method</p>
                <p className="font-medium">{event.attack_method || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Deaths</p>
                <p className="font-medium text-red-500">{event.deaths}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Injuries</p>
                <p className="font-medium text-orange-500">{event.injuries}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Metadata */}
        <Card>
          <CardHeader>
            <CardTitle>Metadata</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Event ID</p>
                <p className="font-mono text-xs">{event.event_id}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Extraction Method</p>
                <p>{event.extraction_method || '-'}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Created</p>
                <p>{new Date(event.created_at).toLocaleString()}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Annotator</p>
                <p>{event.annotator_name || '-'}</p>
              </div>
            </div>
            {event.notes && (
              <div className="pt-2">
                <p className="text-sm text-muted-foreground">Notes</p>
                <p className="text-sm">{event.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Edit Modal */}
      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Event</DialogTitle>
            <DialogDescription>
              Make changes to the event details. Click save when you're done.
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            {/* Event Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Event Description</Label>
              <Textarea
                id="description"
                value={editForm.event_description}
                onChange={(e) => setEditForm({ ...editForm, event_description: e.target.value })}
                rows={3}
              />
            </div>

            {/* WHO */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="actor">Perpetrator/Actor</Label>
                <Input
                  id="actor"
                  value={editForm.actor_normalized}
                  onChange={(e) => setEditForm({ ...editForm, actor_normalized: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="victim">Victim</Label>
                <Input
                  id="victim"
                  value={editForm.victim_normalized}
                  onChange={(e) => setEditForm({ ...editForm, victim_normalized: e.target.value })}
                />
              </div>
            </div>

            {/* WHERE */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="country">Country</Label>
                <Input
                  id="country"
                  value={editForm.location_country}
                  onChange={(e) => setEditForm({ ...editForm, location_country: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="city">City</Label>
                <Input
                  id="city"
                  value={editForm.location_city}
                  onChange={(e) => setEditForm({ ...editForm, location_city: e.target.value })}
                />
              </div>
            </div>

            {/* WHEN */}
            <div className="space-y-2">
              <Label htmlFor="date">Date (YYYY-MM-DD)</Label>
              <Input
                id="date"
                type="date"
                value={editForm.date_normalized}
                onChange={(e) => setEditForm({ ...editForm, date_normalized: e.target.value })}
              />
            </div>

            {/* WHAT - Taxonomy */}
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="taxonomy1">Taxonomy Level 1</Label>
                <Select
                  value={editForm.taxonomy_l1}
                  onValueChange={(value) => setEditForm({ ...editForm, taxonomy_l1: value })}
                >
                  <SelectTrigger id="taxonomy1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Violence against civilians">Violence against civilians</SelectItem>
                    <SelectItem value="Battles">Battles</SelectItem>
                    <SelectItem value="Explosions/Remote violence">Explosions/Remote violence</SelectItem>
                    <SelectItem value="Riots">Riots</SelectItem>
                    <SelectItem value="Protests">Protests</SelectItem>
                    <SelectItem value="Strategic developments">Strategic developments</SelectItem>
                    <SelectItem value="Unknown">Unknown</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="taxonomy2">Taxonomy Level 2</Label>
                <Input
                  id="taxonomy2"
                  value={editForm.taxonomy_l2}
                  onChange={(e) => setEditForm({ ...editForm, taxonomy_l2: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="taxonomy3">Taxonomy Level 3</Label>
                <Input
                  id="taxonomy3"
                  value={editForm.taxonomy_l3}
                  onChange={(e) => setEditForm({ ...editForm, taxonomy_l3: e.target.value })}
                />
              </div>
            </div>

            {/* HOW */}
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="weapon">Weapon Category</Label>
                <Input
                  id="weapon"
                  value={editForm.weapon_category}
                  onChange={(e) => setEditForm({ ...editForm, weapon_category: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="deaths">Deaths</Label>
                <Input
                  id="deaths"
                  type="number"
                  min="0"
                  value={editForm.deaths}
                  onChange={(e) => setEditForm({ ...editForm, deaths: parseInt(e.target.value) || 0 })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="injuries">Injuries</Label>
                <Input
                  id="injuries"
                  type="number"
                  min="0"
                  value={editForm.injuries}
                  onChange={(e) => setEditForm({ ...editForm, injuries: parseInt(e.target.value) || 0 })}
                />
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setEditOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveEdit} disabled={saving}>
              {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Mark Reviewed Dialog */}
      <Dialog open={unflagOpen} onOpenChange={setUnflagOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Mark as Reviewed</DialogTitle>
            <DialogDescription>
              This will remove the flag from this event. You can optionally add notes about your review.
            </DialogDescription>
          </DialogHeader>

          <div className="py-4">
            <div className="space-y-2">
              <Label htmlFor="reviewNotes">Review Notes (optional)</Label>
              <Textarea
                id="reviewNotes"
                placeholder="Add any notes about your review..."
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                rows={3}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setUnflagOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUnflag} className="bg-green-600 hover:bg-green-700">
              Complete Review
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

// Error boundary for when event is not found
export function ErrorBoundary() {
  const navigate = useNavigate()

  return (
    <div className="space-y-4">
      <Button variant="ghost" onClick={() => navigate('/events')}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Events
      </Button>
      <div className="rounded-lg bg-destructive/10 p-4 text-destructive">
        Event not found or failed to load
      </div>
    </div>
  )
}
