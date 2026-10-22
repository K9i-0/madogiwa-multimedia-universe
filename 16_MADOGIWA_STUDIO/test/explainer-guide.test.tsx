import { env } from "cloudflare:workers";
import { SELF } from "cloudflare:test";
import { renderToStaticMarkup } from "react-dom/server";
import { expect, it } from "vitest";
import { createEpisode, updateEpisode } from "../worker/repository";
import { applyYouTubeStatus, registerYouTube, youtubeRegistrationSchema } from "../worker/youtube";
import { readyVideo } from "./youtube-fixture";
import { loadPublicEpisode } from "../src/server/public-data.server";
import { getExplainerGuide } from "../src/server/explainer-guides";
import { ExplainerGuide } from "../src/components/explainer-guide";

it("only attaches reviewed guides to the corresponding public video", () => {
  expect(getExplainerGuide("codex-tripo-3d-character-workflow", ["another-id"])).toBeUndefined();
  expect(getExplainerGuide("unknown", ["hCWMw1nB43A"])).toBeUndefined();
  expect(getExplainerGuide("__proto__", ["hCWMw1nB43A"])).toBeUndefined();
  const guide = getExplainerGuide("codex-tripo-3d-character-workflow", ["hCWMw1nB43A"])!;
  expect(guide.markdown).toContain("720p");
  expect(guide.markdown).toContain("1080p");
  const html = renderToStaticMarkup(<ExplainerGuide slug="codex-tripo-3d-character-workflow" markdown={guide.markdown} workflow={guide.workflow} />);
  expect(html).toContain("AIへの指示をコピー");
  expect(html).toContain("AIへの指示のMarkdown原文");
  expect(html).toContain("動画資料のMarkdown原文");
  expect(html).not.toContain('class="document-markdown"');
  expect(guide.workflow).toContain("Tripoによる3D生成は必須");
  expect(guide.workflow).toContain("回転動画はWanに限定しません");
  expect(html).not.toContain("AI用URLをコピー");
  expect(html).toContain("リグとウェイト");
  expect(html).toContain("/episodes/codex-tripo-3d-character-workflow/guide.md");
});

it("serves identical Markdown and SSR content, keeps private notes private, and revokes archived access", async () => {
  const slug = "coding-ai-wan-video-workflow";
  const episode = await createEpisode(env.DB, { slug, title: "Wan guide" }, "test");
  const url = `http://localhost/episodes/${slug}/guide.md`;
  expect((await SELF.fetch(url)).status).toBe(404);
  const row = await registerYouTube(env.DB, youtubeRegistrationSchema.parse({ episodeId: episode.id, youtubeId: "RMWefLVS9vQ", contentKind: "explainer", productionNotes: false }), "test");
  expect((await SELF.fetch(url)).status).toBe(404);
  await applyYouTubeStatus(env.DB, row, readyVideo(row.youtube_id));
  const detail = await loadPublicEpisode(slug);
  expect(detail?.productions).toEqual([]);
  const response = await SELF.fetch(url);
  expect(response.status).toBe(200);
  expect(response.headers.get("content-type")).toBe("text/markdown; charset=utf-8");
  expect(await response.text()).toBe(detail?.guide?.markdown);
  const workflowUrl = `http://localhost/episodes/${slug}/workflow.md`;
  const workflowResponse = await SELF.fetch(workflowUrl);
  expect(workflowResponse.status).toBe(200);
  expect(workflowResponse.headers.get("content-type")).toBe("text/markdown; charset=utf-8");
  expect(await workflowResponse.text()).toBe(detail?.guide?.workflow);
  expect(detail?.guide?.markdown).toContain(`/episodes/${slug}/workflow.md`);
  const html = await (await SELF.fetch(`http://localhost/episodes/${slug}`)).text();
  expect(html).toContain('type="text/markdown"');
  expect(html).toContain("この方法で作る");
  expect(html).toContain("映像が採用できる場合");
  await updateEpisode(env.DB, episode.id, { status: "archived" });
  expect((await SELF.fetch(url)).status).toBe(404);
  expect((await SELF.fetch(workflowUrl)).status).toBe(404);
  expect((await SELF.fetch("http://localhost/episodes/missing/guide.md")).status).toBe(404);
}, 20000);


it.each([
  ["codex-tripo-3d-character-workflow", "hCWMw1nB43A"],
  ["codex-animated-line-stickers", "PJ3ak1m-Itg"],
])("only serves execution instructions for matching public video %s", async (slug, youtubeId) => {
  const url = `http://localhost/episodes/${slug}/workflow.md`;
  expect((await SELF.fetch(url)).status).toBe(404);
  const episode = await createEpisode(env.DB, { slug, title: "Tripo workflow" }, "test");
  const row = await registerYouTube(env.DB, youtubeRegistrationSchema.parse({ episodeId: episode.id, youtubeId, contentKind: "explainer", productionNotes: false }), "test");
  expect((await SELF.fetch(url)).status).toBe(404);
  await applyYouTubeStatus(env.DB, row, readyVideo(row.youtube_id));
  const response = await SELF.fetch(url);
  expect(response.headers.get("content-type")).toBe("text/markdown; charset=utf-8");
  const detail = await loadPublicEpisode(slug);
  expect(await response.text()).toBe(detail?.guide?.workflow);
  const html = await (await SELF.fetch(`http://localhost/episodes/${slug}`)).text();
  expect(html).toContain("この方法で作る");
  expect(detail?.guide?.workflow).toBeTruthy();
  expect(detail?.guide?.markdown).toContain(`/episodes/${slug}/workflow.md`);
  expect(html).toContain(`/episodes/${slug}/workflow.md`);
  await updateEpisode(env.DB, episode.id, { status: "archived" });
  expect((await SELF.fetch(url)).status).toBe(404);
  expect((await SELF.fetch("http://localhost/episodes/missing/workflow.md")).status).toBe(404);
});
