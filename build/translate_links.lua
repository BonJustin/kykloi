-- translate_links.lua
-- 1. Rewrites relative markdown links (.md) to HTML (.html)
-- 2. If KYKLOI_SECURE_BUILD is active, rewrites image sources to append .enc

local is_secure = os.getenv("KYKLOI_SECURE_BUILD") == "1"

function Link(el)
  -- Skip absolute URLs or protocols
  if el.target:match("^%a+://") or el.target:match("^//") or el.target:match("^mailto:") then
    return el
  end

  -- Decode URL to inspect extension if encoded
  local target = el.target

  -- Separate path from anchor or query
  local path, rest = target:match("^(.-)%.md([#?].*)$")
  if not path then
    path = target:match("^(.-)%.md$")
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

  -- Skip absolute URLs, protocols, or existing data URIs
  if el.src:match("^%a+://") or el.src:match("^//") or el.src:match("^data:") then
    return el
  end

  -- Extract clean base URL ignoring anchors or query parameters
  local base_src, suffix = el.src:match("^(.-)(%?.*)$")
  if not base_src then
    base_src = el.src
    suffix = ""
  end

  -- Append .enc if not already present
  if not base_src:match("%.enc$") then
    el.src = base_src .. ".enc" .. suffix
  end

  el.attributes["data-encrypted-media"] = "true"
  return el
end
