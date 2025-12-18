import { useRouteError, isRouteErrorResponse, useNavigate } from 'react-router'
import { AlertCircle, RefreshCw, ArrowLeft, Home } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'

export function RouteErrorBoundary() {
  const error = useRouteError()
  const navigate = useNavigate()

  let title = 'Something went wrong'
  let description = 'An unexpected error occurred'
  let statusCode: number | null = null

  if (isRouteErrorResponse(error)) {
    statusCode = error.status
    switch (error.status) {
      case 404:
        title = 'Page Not Found'
        description = "The page you're looking for doesn't exist or has been moved."
        break
      case 401:
        title = 'Unauthorized'
        description = 'You need to be logged in to access this page.'
        break
      case 403:
        title = 'Forbidden'
        description = "You don't have permission to access this page."
        break
      case 500:
        title = 'Server Error'
        description = 'The server encountered an error. Please try again later.'
        break
      default:
        description = error.statusText || description
    }
  } else if (error instanceof Error) {
    description = error.message
  }

  return (
    <div className="flex items-center justify-center min-h-[50vh]">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10">
            <AlertCircle className="h-8 w-8 text-destructive" />
          </div>
          {statusCode && (
            <div className="text-5xl font-bold text-muted-foreground mb-2">
              {statusCode}
            </div>
          )}
          <CardTitle className="text-xl">{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-2">
          <Button onClick={() => window.location.reload()} variant="default">
            <RefreshCw className="mr-2 h-4 w-4" />
            Try Again
          </Button>
          <Button onClick={() => navigate(-1)} variant="outline">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Go Back
          </Button>
          <Button onClick={() => navigate('/')} variant="ghost">
            <Home className="mr-2 h-4 w-4" />
            Go to Dashboard
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

// Generic error display for non-route errors
export function ErrorDisplay({
  title = 'Error',
  message = 'Something went wrong',
  onRetry,
}: {
  title?: string
  message?: string
  onRetry?: () => void
}) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10">
        <AlertCircle className="h-6 w-6 text-destructive" />
      </div>
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="mt-1 text-sm text-muted-foreground max-w-sm">{message}</p>
      {onRetry && (
        <Button onClick={onRetry} variant="outline" className="mt-4">
          <RefreshCw className="mr-2 h-4 w-4" />
          Try Again
        </Button>
      )}
    </div>
  )
}
