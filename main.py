from storage import MongoStorage, ValkeyDedupeStorage
from parser_factory import ParserService

# twitter_sample = {
#     "data": [ 
#         {
#             "text": "🦅 https://t.co/FnR3dqIWtL", 
#             "created_at": "2024-10-16T12:58:35.000Z", 
#             "id": "1846536216969089037", 
#             "public_metrics": { 
#                 "retweet_count": 0, 
#                 "reply_count": 0, 
#                 "like_count": 0, 
#                 "quote_count": 0, 
#                 "bookmark_count": 0, 
#                 "impression_count": 12 
#             }, 
#             "edit_history_tweet_ids": [ "1846536216969089037" ] 
#         } 
#     ],
#     "meta": { 
#         "result_count": 1, 
#         "newest_id": "1846536216969089037", 
#         "oldest_id": "1846536216969089037" 
#     } 
# }

# facebook_sample = { 
#                    "data": 
#                        [ 
#                         { 
#                          "id": "4365615057102193_4264667337196966", 
#                          "created_time": "2025-05-17T12:37:18+0000", 
#                          "permalink_url": "https://www.facebook.com/4365615057102193/posts/4264667337196966", 
#                          "attachments": { 
#                              "data": [ 
#                                  { "media_type": "link" } 
#                                 ] 
#                             }, 
#                          "reactions": { 
#                              "data": [ ], 
#                              "summary": { 
#                                  "total_count": 0, 
#                                  "viewer_reaction": "NONE" 
#                                 } 
#                             }, 
#                          "comments": { 
#                              "data": [ ], 
#                              "summary": { 
#                                  "order": "chronological", 
#                                  "total_count": 0, 
#                                  "can_comment": True 
#                                 } 
#                             } 
#                         } 
#                     ], 
#                     "paging": {} 
#                 }

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Union

from storage import MongoStorage, ValkeyDedupeStorage
from parser_factory import ParserService

# ---------------- Pydantic Schemas ----------------

# Twitter Schemas
class PublicMetrics(BaseModel):
    retweet_count: int
    reply_count: int
    like_count: int
    quote_count: int
    bookmark_count: Optional[int] = 0
    impression_count: Optional[int] = 0

class TwitterDataItem(BaseModel):
    id: str
    text: str
    created_at: str
    public_metrics: PublicMetrics
    edit_history_tweet_ids: List[str]

class TwitterMeta(BaseModel):
    result_count: int
    newest_id: str
    oldest_id: str

class TwitterPayload(BaseModel):
    data: List[TwitterDataItem]
    meta: TwitterMeta

# Facebook Schemas
class FacebookAttachmentItem(BaseModel):
    media_type: str

class FacebookAttachments(BaseModel):
    data: List[FacebookAttachmentItem]

class FacebookSummary(BaseModel):
    total_count: int
    viewer_reaction: Optional[str] = "NONE"
    order: Optional[str] = None
    can_comment: Optional[bool] = None

class FacebookReactions(BaseModel):
    data: List[Dict[str, Any]]
    summary: FacebookSummary

class FacebookComments(BaseModel):
    data: List[Dict[str, Any]]
    summary: FacebookSummary

class FacebookDataItem(BaseModel):
    id: str
    created_time: str
    permalink_url: str
    attachments: FacebookAttachments
    reactions: FacebookReactions
    comments: FacebookComments

class FacebookPayload(BaseModel):
    data: List[FacebookDataItem]
    paging: Optional[Dict[str, Any]] = {}

# Unified request schema
class ParseAndPushRequest(BaseModel):
    platform: str = Field(..., description="Platform name: twitter or facebook")
    payload: Dict[str, Any]

    @field_validator("platform")
    def check_platform(cls, v):
        v_lower = v.lower()
        if v_lower not in ["twitter", "facebook"]:
            raise ValueError("platform must be 'twitter' or 'facebook'")
        return v_lower
    

# ---------------- FastAPI App ----------------

app = FastAPI(title="Social Media Parser API")


# Initialize storage and parser once
storage = MongoStorage()
dedupe = ValkeyDedupeStorage()
parser_service = ParserService.ParserService(storage, dedupe)

@app.post("/parse-and-push")
def parse_and_push(req: ParseAndPushRequest):
    platform = req.platform
    payload_dict = req.payload

    # Validate payload based on platform
    try:
        if platform == "twitter":
            TwitterPayload(**payload_dict)
        elif platform == "facebook":
            FacebookPayload(**payload_dict)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid payload for {platform}: {e}")

    try:
        inserted, skipped = parser_service.process_raw(platform, payload_dict)
        return {"platform": platform, "inserted": inserted, "skipped": skipped}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# def main():
#     # run demo 
#     storage = MongoStorage() 
#     dedupe = ValkeyDedupeStorage() 
#     service = ParserService.ParserService(storage, dedupe)
    
#     ins_t, skip_t = service.process_raw("twitter", twitter_sample) 
#     ins_f, skip_f = service.process_raw("facebook", facebook_sample)

#     print(f"Twitter inserted={ins_t} skipped={skip_t}") 
#     print(f"Facebook inserted={ins_f} skipped={skip_f}")

# if __name__ == "__main__":
#     main()
