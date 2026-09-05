# Search providers

`BingVisualSearchProvider` submits the user’s uploaded image to Bing Visual Search when `BING_VISUAL_SEARCH_KEY` is configured. It parses provider-returned result fields into candidates. When no key is present, `UnconfiguredSearchProvider` returns no results and explicitly reports its status. No sample celebrity/person results are hardcoded.

