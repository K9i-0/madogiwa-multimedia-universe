import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/episodes/$slug_/workflow.md")({
  server: { handlers: { GET: async ({ params }) => {
    const { loadPublicEpisode } = await import("@/server/public-data.server");
    const detail = await loadPublicEpisode(params.slug);
    if (!detail?.guide?.workflow) return new Response("Not found", { status: 404, headers: { "cache-control": "no-store" } });
    return new Response(detail.guide.workflow, { headers: {
      "content-type": "text/markdown; charset=utf-8",
      "cache-control": "no-store",
      "x-content-type-options": "nosniff",
      "link": `<https://madogiwa.work/episodes/${encodeURIComponent(params.slug)}>; rel="canonical"`,
    } });
  } } },
});
