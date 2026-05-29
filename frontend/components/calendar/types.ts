export interface CalendarPost {
  id: string;
  client_id: string;
  campaign_id: string | null;
  scheduled_at: string;
  format: "IMAGE" | "CAROUSEL" | "REEL";
  caption: string | null;
  hashtags: string[] | null;
  status: "PROGRAMADO" | "PUBLICADO" | "FALLIDO";
}
