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
status: "available"  # available, sold, price_on_request
category: "Abstract"  # Abstract or Surrealistisch
featured: false
weight: 100

# Image (relative to assets/ — update subdirectory to match category)
image: "images/paintings/abstract/{{ .File.ContentBaseName }}.jpg"
---

Beschrijving van het werk.
