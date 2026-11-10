-- translate_links.lua
-- 1. Rewrites relative markdown links (.md) to HTML (.html)
-- 2. If KYKLOI_SECURE_BUILD is active, rewrites image sources to append .enc
-- 3. Transforms Obsidian/GitHub callouts (> [!TYPE]) into semantic HTML5 <aside> tags (Zero CSS classes injected)

local is_secure = os.getenv("KYKLOI_SECURE_BUILD") == "1"

function Link(el)
  -- Skip absolute URLs or protocols
  if el.target:match("^%a+://") or el.target:match("^//") or el.target:match("^mailto:") then
    return el
  end

  -- Separate path from anchor or query
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

function BlockQuote(el)
  if #el.content == 0 then
    return el
  end

  local first_block = el.content[1]
  if first_block.t ~= "Para" or #first_block.content == 0 then
    return el
  end

  local first_inline = first_block.content[1]
  if first_inline.t ~= "Str" then
    return el
  end

  -- Match [!TYPE]
  local callout_type = first_inline.text:match("^%!%[([%a%-_]+)%]")
  if not callout_type then
    return el
  end

  -- Extract optional custom title from subsequent inlines in the first paragraph
  local title_inlines = {}
  local content_blocks = {}

  for i = 2, #first_block.content do
    table.insert(title_inlines, first_block.content[i])
  end

  local callout_title = ""
  if #title_inlines > 0 then
    callout_title = pandoc.utils.stringify(title_inlines):gsub("^%s+", "")
  end
  if callout_title == "" then
    callout_title = callout_type:gsub("^%l", string.upper)
  end

  -- Collect remaining body blocks
  for i = 2, #el.content do
    table.insert(content_blocks, el.content[i])
  end

  -- Render as purely semantic HTML5 <aside> with <header> (No CSS classes)
  local header_html = string.format("<header><strong>%s</strong></header>", pandoc.utils.stringify(callout_title))

  local aside_blocks = {
    pandoc.RawBlock("html", "<aside>"),
    pandoc.RawBlock("html", header_html)
  }

  for _, b in ipairs(content_blocks) do
    table.insert(aside_blocks, b)
  end

  table.insert(aside_blocks, pandoc.RawBlock("html", "</aside>"))
  return aside_blocks
end
