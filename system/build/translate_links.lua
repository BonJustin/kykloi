local is_secure = os.getenv("KYKLOI_SECURE_BUILD") == "1"

local function is_external(url)
  return url:match("^%a+://") ~= nil or url:match("^//") ~= nil or url:match("^mailto:") ~= nil
end

function Link(el)
  -- Bypass external protocols and pure in-page anchors immediately
  if is_external(el.target) or el.target:sub(1, 1) == "#" or el.target:sub(1, 1) == "?" then
    return el
  end

  local path, separator, suffix = el.target:match("^([^#?]+)([#?])(.*)$")
  if not path then
    path = el.target
    separator = ""
    suffix = ""
  end

  -- If path component is empty, it is an in-page query or fragment
  if path == "" then
    return el
  end

  local ext = path:match("%.([a-zA-Z0-9]+)$")
  if ext then
    local lower_ext = ext:lower()
    if lower_ext == "md" or lower_ext == "markdown" then
      path = path:sub(1, -#ext - 2) .. ".html"
      el.target = path .. separator .. suffix
    end
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
