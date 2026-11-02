function Link(el)
  -- 1. Skip external protocols (http, https, ftp, mailto, etc.) and protocol-relative URLs (//)
  if el.target:match("^%a+://") or el.target:match("^//") or el.target:match("^mailto:") then
    return el
  end

  -- 2. Case A: Path ending in .md with an anchor (#) or query string (?)
  local path, rest = el.target:match("^(.-)%.md([#?].*)$")

  -- 3. Case B: Path ending purely in .md
  if not path then
    path = el.target:match("^(.-)%.md$")
    rest = ""
  end

  -- 4. Rewrite the target if a match was found
  if path then
    el.target = path .. ".html" .. rest
  end

  return el
end
