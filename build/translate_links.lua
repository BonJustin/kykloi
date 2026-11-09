-- translate_links.lua
-- 1. Rewrites relative markdown links (.md) to HTML (.html)
-- 2. If KYKLOI_SECURE_BUILD is active, rewrites image sources to append .enc

local is_secure = os.getenv("KYKLOI_SECURE_BUILD") == "1"

function Link(el)
  -- Skip absolute URLs or protocols
  if el.target:match("^%a+://") or el.target:match("^//") or el.target:match("^mailto:") then
    return el
  end

  local path, rest = el.target:match("^(.-)%.md([#?].*)$")
  if not path then
    path = el.target:match("^(.-)%.md$")
    rest = ""
  end

  if path then
    el.target = path .. ".html" .. rest
  end

  return el
end

function Image(el)
  if not is_secure then
    return el
  end

  -- Skip absolute URLs or protocols or existing data URIs
  if el.src:match("^%a+://") or el.src:match("^//") or el.src:match("^data:") then
    return el
  end

  -- Append .enc if it doesn't already have it
  if not el.src:match("%.enc$") then
    el.src = el.src .. ".enc"
  end

  el.attributes["data-encrypted-media"] = "true"
  return el
end
