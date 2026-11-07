function Link(el)
  if el.target:match("^%a+://") or el.target:match("^//") or el.target:match("^mailto:") then
    return el
  end

  local path, rest = el.target:match("^(.-)%.md([#?].*)$")

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
