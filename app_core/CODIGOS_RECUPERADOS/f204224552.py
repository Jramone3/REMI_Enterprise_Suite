erde-1.0.171/src/de/mod.rs` as u128tracing::span-- ;&next_core::next_app::AppPage
 span=tracing::span::active<- -> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/string_cache-0.8.7/src/atom.rsMapAccess::next_value called before next_key/root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/serde-1.0.171/src/de/value.rsdefaultapply$$boundconcat$$ACTION_ARG_/build/packages/next-swc/crates/core/src/server_actions.rscreateServerReferenceprivate-next-rsc-action-client-wrapperensureServerEntryExportscreateActionProxyprivate-next-rsc-action-proxy/root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/futures-util-0.3.28/src/future/join_all.rsicojpgpngsvgapple-iconopengraph-imagegiftwitter-imagesitemapxmlfaviconwebmanifestrobotstxt/packages/next-swc/crates/next-core/src/next_app/metadata/mod.rs.webmanifestempty segments are not allowed[[...]]slashes are not allowed in segmentsroute, this page path already has the final PageType appended (segments: ), catch all segment must be the last segment (segments: packages/next-swc/crates/next-core/src/next_edge/route_regex.rs\[((?:\[.*\])|.+)\],packages/next-swc/crates/next-core/src/next_font/local/font_fallback.rsMissing transform value for package packages/next-swc/crates/next-core/src/next_shared/transforms/modularize_imports.rsnext_dev=tracenext_core=tracenext_font=traceturbopack_node=trace$CARGO_MANIFEST_DIR/js/src$CARGO_MANIFEST_DIRpackages/next-swc/crates/next-core/src/embed_js.rsassertion failed: !\"$CARGO_MANIFEST_DIR/js/src\".replace(\"$CARGO_MANIFEST_DIR\", \"\").contains(\'$\')buildbuild/clientbuild/client/app-bootstrap.ts/**
 * This is the runtime entry point for Next.js App Router client-side bundles.
 */

import '../shims'
import { appBootstrap } from 'next/dist/client/app-bootstrap'

appBootstrap(() => {
  require('./app-turbopack')
  const { hydrate } = require('./app-index')
  hydrate()
})
build/client/app-turbopack.ts// eslint-disable-next-line no-undef
self.__next_require__ = __turbopack_require__

// @ts-ignore
// eslint-disable-next-line no-undef
;(self as any).__next_chunk_load__ = __turbopack_load__
build/client/bootstrap.ts/**
 * This is the runtime entry point for Next.js Page Router client-side bundles.
 */

import '../shims'
import { initialize, hydrate, version, router, emitter } from 'next/dist/client'

declare global {
  interface Window {
    next: any
  }
}

window.next = {
  version: `${version}-turbo`,
  // router is initialized later so it has to be live-binded
  get router() {
    return router
  },
  emitter,
}
;(self as any).__next_set_public_path__ = () => {}

initialize({})
  .then(() => hydrate())
  .catch(console.error)
build/serverbuild/server/app-bootstrap.ts/**
 * This is the runtime entry point for Next.js App Router server-side bundles.
 */

import '../shims'
build/shims.ts// This ensures Next.js uses React 18's APIs (hydrateRoot) instead of React 17's
// (hydrate).
process.env.__NEXT_REACT_ROOT = 'true'
entryentry/configentry/config/next.jsimport loadConfig from 'next/dist/server/config'
import loadCustomRoutes from 'next/dist/lib/load-custom-routes'
import { PHASE_DEVELOPMENT_SERVER } from 'next/dist/shared/lib/constants'
import assert from 'node:assert'

const loadNextConfig = async (silent) => {
  const nextConfig = await loadConfig(
    PHASE_DEVELOPMENT_SERVER,
    process.cwd(),
    undefined,
    undefined,
    silent
  )

  nextConfig.generateBuildId = await nextConfig.generateBuildId?.()

  const customRoutes = await loadCustomRoutes(nextConfig)

  // TODO: these functions takes arguments, have to be supported in a different way
  nextConfig.exportPathMap = nextConfig.exportPathMap && {}
  nextConfig.webpack = nextConfig.webpack && {}

  // Transform the `modularizeImports` option
  nextConfig.modularizeImports = nextConfig.modularizeImports
    ? Object.fromEntries(
        Object.entries(nextConfig.modularizeImports).map(([mod, config]) => [
          mod,
          {
            ...config,
            transform:
              typeof config.transform === 'string'
                ? config.transform
                : Object.entries(config.transform).map(([key, value]) => [
                    key,
                    value,
                  ]),
          },
        ])
      )
    : undefined

  if (nextConfig.experimental?.turbopack?.loaders) {
    ensureLoadersHaveSerializableOptions(
      nextConfig.experimental.turbopack.loaders
    )
  }

  return {
    customRoutes: customRoutes,
    config: nextConfig,
  }
}

export { loadNextConfig as default }

function ensureLoadersHaveSerializableOptions(turbopackLoaders) {
  for (const [ext, loaderItems] of Object.entries(turbopackLoaders)) {
    for (const loaderItem of loaderItems) {
      if (
        typeof loaderItem !== 'string' &&
        !deepEqual(loaderItem, JSON.parse(JSON.stringify(loaderItem)))
      ) {
        throw new Error(
          `loader ${loaderItem.loader} for match "${ext}" does not have serializable options. Ensure that options passed are plain JavaScript objects and values.`
        )
      }
    }
  }
}

function deepEqual(a, b) {
  try {
    assert.deepStrictEqual(a, b)
    return true
  } catch {
    return false
  }
}
entry/page-loader.ts// inserted by rust code
declare const PAGE_PATH: string

  // Adapted from https://github.com/vercel/next.js/blob/canary/packages/next/build/webpack/loaders/next-client-pages-loader.ts
;(window.__NEXT_P = window.__NEXT_P || []).push([
  PAGE_PATH,
  () => {
    return require('PAGE')
  },
])
if (module.hot) {
  module.hot.dispose(function () {
    window.__NEXT_P.push([PAGE_PATH])
  })
}
entry/pagesentry/pages/_app.tsxexport * from '@vercel/turbopack-next/pages/_app'
export { default } from '@vercel/turbopack-next/pages/_app'
entry/pages/_document.tsxexport * from '@vercel/turbopack-next/pages/_document'
export { default } from '@vercel/turbopack-next/pages/_document'
entry/pages/_error.tsxexport * from '@vercel/turbopack-next/pages/_error'
export { default } from '@vercel/turbopack-next/pages/_error'
next_js_file_path^(icon|apple-icon|opengraph-image|twitter-image)(\d+)$-.StaticDynamicGroupPageSegmentvariant identifiervariant index 0 <= i < 7invalid discriminant for PageSegmentinvalid task input type, expected listmissing discriminant for PageSegmentmissing element for field_0Routevariant index 0 <= i < 2enum PageTypeinvalid discriminant for PageTypemissing discriminant for PageTypeAppPagetuple struct AppPagePathSegmentvariant index 0 <= i < 4AppPathtuple struct AppPathNextFontIssuetitledescriptionstruct NextFontIssuepackages/next-swc/crates/next-core/src/next_font/issue.rsdbgdbg_depth<NextFontIssue as turbo_tasks :: debug :: ValueDebug>::dbg<NextFontIssue as turbo_tasks :: debug :: ValueDebug>::dbg_depthfile_path<NextFontIssue as Issue>::category<NextFontIssue as Issue>::severity<NextFontIssue as Issue>::file_path<NextFontIssue as Issue>::title<NextFontIssue as Issue>::descriptionnode_modules/