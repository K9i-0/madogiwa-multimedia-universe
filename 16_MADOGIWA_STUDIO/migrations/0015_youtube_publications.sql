ALTER TABLE episodes ADD COLUMN content_kind TEXT NOT NULL DEFAULT 'story' CHECK(content_kind IN ('story','explainer','music','other'));
ALTER TABLE episodes ADD COLUMN production_notes_enabled INTEGER NOT NULL DEFAULT 1 CHECK(production_notes_enabled IN (0,1));
CREATE TABLE youtube_publications (
 id TEXT PRIMARY KEY,
 episode_id TEXT NOT NULL REFERENCES episodes(id),
 generation_id TEXT REFERENCES generations(id),
 legacy_video_id TEXT REFERENCES videos(id),
 youtube_id TEXT NOT NULL UNIQUE CHECK(length(youtube_id)=11),
 state TEXT NOT NULL DEFAULT 'pending' CHECK(state IN ('pending','processing','waiting_public','ready','unavailable','failed')),
 is_active INTEGER NOT NULL DEFAULT 0,
 is_featured INTEGER NOT NULL DEFAULT 0,
 thumbnail_url TEXT,
 youtube_title TEXT,
 privacy_status TEXT,
 processing_status TEXT,
 embeddable INTEGER NOT NULL DEFAULT 0,
 checked_at TEXT,
 created_at TEXT NOT NULL,
 created_by TEXT
);
CREATE INDEX youtube_publications_episode ON youtube_publications(episode_id,created_at);
CREATE UNIQUE INDEX youtube_publications_active ON youtube_publications(episode_id) WHERE is_active=1;
CREATE TRIGGER youtube_insert_revision AFTER INSERT ON youtube_publications BEGIN UPDATE public_content_revision SET revision=lower(hex(randomblob(16))) WHERE id=1; END;
CREATE TRIGGER youtube_update_revision AFTER UPDATE ON youtube_publications BEGIN UPDATE public_content_revision SET revision=lower(hex(randomblob(16))) WHERE id=1; END;
CREATE TRIGGER youtube_delete_revision AFTER DELETE ON youtube_publications BEGIN UPDATE public_content_revision SET revision=lower(hex(randomblob(16))) WHERE id=1; END;
CREATE VIEW published_youtube_videos AS SELECT COALESCE(p.legacy_video_id,p.id) AS id,p.episode_id,p.generation_id,p.youtube_id,
 p.thumbnail_url AS poster_url,NULL AS poster_r2_key,p.is_featured,p.created_at,0 AS display_order,'published' AS status,p.youtube_title AS label
 FROM youtube_publications p WHERE p.is_active=1 AND p.state='ready';
