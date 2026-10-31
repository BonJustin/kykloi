function Link(el)
  -- Skip external protocols and protocol-relative URLs
  if el.target:match("^%a+://") or el.target:match("^//") then
    return el
  end

  -- Target ending in .md or .md followed immediately by #anchor or ?query
  if el.target:match("%.md$") or el.target:match("%.md([#?].*)$") then
    el.target = el.target:gsub("(%w+)%.md([#?]?)", "%1.html%2", 1)
  end
  return el
end
