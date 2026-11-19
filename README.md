# מה מבשלים — family recipes

One Markdown file per recipe in `recipes/`. `python3 build.py` turns them into a single page, `docs/index.html`, that works offline-ish on a phone (search, filters, tick-off ingredients, keep-screen-on, share link).

## Recipe file format

```markdown
---
title: פתיתים קלאסיים
emoji: 🍚
tags: [תוספת, פתיתים, מהיר, לילדים]
time: 25 דקות
servings: 2–4
source: https://example.com/recipe   (optional)
status: tried                        (tried = we made it and liked it, new = to try)
---

## מצרכים
- 1 כוס פתיתים

### תת-כותרת (optional, e.g. לרוטב)
- ...

## אופן ההכנה
1. ...

## טיפים
- ...
```

Tags used by the filter chips: לילדים, למבוגרים, עוף, בשר, דגים, צמחוני, פתיתים, פסטה, מרק, תוספת, מהיר, סיר אחד, תנור, נינג׳ה, קינוח.

## Adding or changing a recipe

1. Add or edit a file in `recipes/` (or paste a recipe to Claude and ask it to add one).
2. When the family has made a new recipe and liked it, change `status: new` to `status: tried`.
3. Run `python3 build.py`, then commit and push. GitHub Pages serves `docs/`.
