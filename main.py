from storage import MongoStorage, ValkeyDedupeStorage
from parser_factory import ParserService

twitter_sample = {
    "data": [ 
        {
            "text": "🦅 https://t.co/FnR3dqIWtL", 
            "created_at": "2024-10-16T12:58:35.000Z", 
            "id": "1846536216969089037", 
            "public_metrics": { 
                "retweet_count": 0, 
                "reply_count": 0, 
                "like_count": 0, 
                "quote_count": 0, 
                "bookmark_count": 0, 
                "impression_count": 12 
            }, 
            "edit_history_tweet_ids": [ "1846536216969089037" ] 
        } 
    ],
    "meta": { 
        "result_count": 1, 
        "newest_id": "1846536216969089037", 
        "oldest_id": "1846536216969089037" 
    } 
}

facebook_sample = { 
                   "data": 
                       [ 
                        { 
                         "id": "4365615057102193_4264667337196966", 
                         "created_time": "2025-05-17T12:37:18+0000", 
                         "permalink_url": "https://www.facebook.com/4365615057102193/posts/4264667337196966", 
                         "attachments": { 
                             "data": [ 
                                 { "media_type": "link" } 
                                ] 
                            }, 
                         "reactions": { 
                             "data": [ ], 
                             "summary": { 
                                 "total_count": 0, 
                                 "viewer_reaction": "NONE" 
                                } 
                            }, 
                         "comments": { 
                             "data": [ ], 
                             "summary": { 
                                 "order": "chronological", 
                                 "total_count": 0, 
                                 "can_comment": True 
                                } 
                            } 
                        } 
                    ], 
                    "paging": {} 
                }

def main():
    # run demo 
    storage = MongoStorage() 
    dedupe = ValkeyDedupeStorage() 
    service = ParserService.ParserService(storage, dedupe)
    
    ins_t, skip_t = service.process_raw("twitter", twitter_sample) 
    ins_f, skip_f = service.process_raw("facebook", facebook_sample)

    print(f"Twitter inserted={ins_t} skipped={skip_t}") 
    print(f"Facebook inserted={ins_f} skipped={skip_f}")

if __name__ == "__main__":
    main()
