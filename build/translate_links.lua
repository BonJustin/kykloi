-- translate_links.lua
-- 1. Rewrites relative markdown links (.md) to HTML (.html)
-- 2. Appends .enc to media targets and tags attributes when KYKLOI_SECURE_BUILD is active

local is_secure = os.getenv("KYKLOI_SECURE_BUILD") == "1"

local function is_external(url)
  return url:match("^%a+://") ~= nil or url:match("^//") ~= nil or url:match("^mailto:") ~= nil
end

function Link(el)
  if is_external(el.target) or el.target:sub(1, 1) == "#" then
    return el
  end

  local path, separator, suffix = el.target:match("^([^#?]+)([#?])(.*)$")
  if not path then
    path = el.target
    separator = ""
    suffix = ""
  end

  if path:match("%.md$") then
    path = path:gsub("%.md$", ".html")
    el.target = path .. separator .. suffix
  end

  return el
end

function Image(el)
  if not is_secure or is_external(el.src) or el.src:match("^data:") then
    return el
  end

  local path, separator, suffix = el.src:match("^([^#?]+)([#?])(.*)$")
  if not path then
    path = el.src
    separator = ""
    suffix = ""
  end

  if not path:match("%.enc$") then
    path = path .. ".enc"
    el.src = path .. separator .. suffix
  end

  el.attributes["data-encrypted-media"] = "true"
  return el
end
