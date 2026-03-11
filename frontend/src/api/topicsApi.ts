import { apiGet, apiPost } from "./client";
import type { Topic, TopicReviewRequest } from "../types/source";

export function getTopics(): Promise<Topic[]> {
  return apiGet<Topic[]>("/topics");
}

export function reviewTopic(body: TopicReviewRequest): Promise<Topic> {
  return apiPost<TopicReviewRequest, Topic>("/topics/review", body);
}
