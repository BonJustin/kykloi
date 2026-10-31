function Link(el)
  -- ONLY process links that end in .md AND do NOT start with http
  if el.target:match("%.md(%#?.*)$") and not el.target:match("^http") then
    -- 1. Replace .md with .html
    local new_target = el.target:gsub("%.md", ".html")
    
    el.target = new_target
  end
  return el
end
