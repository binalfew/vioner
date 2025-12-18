import { type RouteConfig, route, index, layout } from "@react-router/dev/routes";

export default [
  // Login page (no layout)
  route("login", "./routes/login.tsx"),

  // App layout wraps all routes (sidebar + main content)
  layout("./routes/_layout.tsx", [
    index("./routes/dashboard.tsx"),
    route("training", "./routes/training.tsx"),
    route("models", "./routes/models.tsx"),
    route("analytics", "./routes/analytics.tsx"),
    route("history", "./routes/history.tsx", [
      route(":id", "./routes/history.$id.tsx"),
    ]),
    route("events", "./routes/data.tsx"),
    route("events/:id", "./routes/events.$id.tsx"),
    route("locations", "./routes/locations.tsx"),
    route("settings", "./routes/settings.tsx"),
  ]),
] satisfies RouteConfig;
