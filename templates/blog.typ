#let post(title: none, date: none, description: "", lang: "en", body) = {
  assert(type(title) == str, message: "post requires a title string")
  assert(type(date) == str, message: "post requires a YYYY-MM-DD date string")
  set text(lang: lang)
  set document(title: title, author: "hikettei", description: description)
  [#metadata((title: title, date: date, description: description)) <blog-post>]

  html.elem("html", attrs: (lang: lang))[
    #html.elem("head")[
      #html.elem("meta", attrs: (charset: "utf-8"))
      #html.elem("meta", attrs: (name: "viewport", content: "width=device-width, initial-scale=1"))
      #html.elem("meta", attrs: (name: "description", content: description))
      #html.elem("meta", attrs: (name: "theme-color", content: "#f8f7f3"))
      #html.elem("title")[#title · hikettei]
      #html.elem("link", attrs: (
        rel: "stylesheet",
        href: "../../style.css?v=" + sys.inputs.at("style-version", default: "dev"),
      ))
    ]
    #html.elem("body")[
      #html.elem("main", attrs: (class: "article-page"))[
        #html.elem("nav", attrs: (class: "article-nav", "aria-label": "Blog navigation"))[
          #html.elem("a", attrs: (href: "../../#blog"), "'(blog)")
          #html.elem("span")[hikettei🌙]
        ]
        #html.elem("article")[
          #html.elem("header", attrs: (class: "article-header"))[
            #html.elem("time", attrs: (datetime: date))[#date]
            #html.elem("h1")[#title]
          ]
          #html.elem("div", attrs: (class: "article-body"))[#body]
        ]
        #html.elem("footer", attrs: (class: "article-footer"))[
          #html.elem("a", attrs: (href: "../../#blog"))[← Back to blog]
        ]
      ]
    ]
  ]
}
