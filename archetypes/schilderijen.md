---
title: "{{ replace .File.ContentBaseName `-` ` ` | title }}"
date: {{ .Date }}
draft: false
translationKey: "{{ .File.ContentBaseName }}"
type: "schilderijen"

# Painting metadata
medium: ""
dimensions: ""
year: ""
price: ""
status: "available"  # available, sold, price_on_request
featured: false
weight: 100

# Image (relative to assets/)
image: "images/paintings/{{ .File.ContentBaseName }}.jpg"
---

Beschrijving van het werk.
