# Collecting ads from the public ad libraries

Both libraries are public and free. Neither offers an API for ordinary commercial ads in the US (Meta's Ad Library API covers political/issue ads and ads delivered in the EU; LinkedIn has no public API for its library). So collection means reading the library pages.

**Terms of use.** Meta and LinkedIn prohibit automated scraping. Use the libraries the way a person would: open pages in the user's own browser session, at a human pace, read what is on screen, and save the creatives you need for this analysis. Don't run bulk downloaders, don't parallelize requests, don't log in on the user's behalf. If in doubt, ask the user to open the pages or paste screenshots.

## Meta Ad Library (Instagram / Facebook)

Base URL: `https://www.facebook.com/ads/library/`

Reliable per-advertiser URL (this survives the library's URL rewriting):
```
https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&media_type=image&search_type=page&view_all_page_id=<PAGE_ID>
```
- Get the `PAGE_ID` from the advertiser's library page (the `view_all_page_id` parameter after clicking the advertiser), not from a text search.
- Always set `country` explicitly. A URL without it resolves to the browser's location and silently returns fewer ads.
- In the US, the library only shows ads **running now** for non-political ads. Your sample is a snapshot of the day: date it.

### Traps that bias a sample without warning
| | Trap | What to do |
|---|---|---|
| a | **Default order is by impressions**, and the URL resets itself. "The first ones" are the ones that spent most. | Note the order you used. For a category snapshot, prefer the most recent start dates. |
| b | **One creative appears in many ads**, up to 10 to 1. | Deduplicate by image content (same picture = same ad), never by ad ID. |
| c | **Text search is contaminated at the top**: searching a brand often returns resellers first. | Search by advertiser page, not by keyword. |
| d | **A brand is not a page.** Big brands run several country pages (e.g. @BrandUSA, @Brand, @BrandUK). | Pick the US page explicitly; if there's no US-labelled page, check "<brand> US" before concluding there isn't one. |
| e | **Franchise locations** have one page each, with near-identical names. | Use the brand's main page, not a location. |
| f | **An empty result is not absence** until you've tried a few name variants ("Citi" vs "Citibank"). | Try 3–4 variants before writing "no ads". |
| g | **"~N results" is not the number of cards you can scroll** (680 declared, 406 listed). | Report what you actually saw. |

### What to keep
- Static images only by default. Carousel/dynamic: first card. Video: skip, or first stable frame if the user wants video included.
- Max 4 ads per advertiser so one heavy spender doesn't define the category.
- Skip job/recruiting ads.

## LinkedIn Ad Library

Base URL: `https://www.linkedin.com/ad-library/`
- Search by advertiser (company page name). Filter by country and date range.
- LinkedIn keeps about a year of ads, so samples are more reproducible than Meta's US snapshot.
- On LinkedIn the platform's interface dominates the unit (text block above, image below), and pictures are usually **framed** rather than full-bleed. That's a property of the platform, not a choice by the advertiser: **never mix LinkedIn and Meta ads in one tally.**
- Code only the creative, not the post text above it (use `words` = `none` when the creative carries no words and everything is in the post text).

## The manifest
Keep `manifest.csv` alongside the images:
```
file,ad_id,advertiser,platform,country,page_url,date_seen,order_used
```
The manifest is what makes the result checkable later. Include it in the report's appendix.
