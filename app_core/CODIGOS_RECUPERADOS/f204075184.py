*
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
next_js_file_pathDevelopmentBuildvariant identifiervariant index 0 <= i < 2enum NextModepackages/next-swc/crates/next-core/src/mode.rs<NextMode as turbo_tasks :: debug :: ValueDebug>::dbg<NextMode as turbo_tasks :: debug :: ValueDebug>::dbg_depthinvalid discriminant for NextModeinvalid task input type, expected listmissing discriminant for NextMode^(icon|apple-icon|opengraph-image|twitter-image)(\d+)$-.StaticDynamicGroupPageSegmentvariant index 0 <= i < 7invalid discriminant for PageSegmentmissing discriminant for PageSegmentmissing element for field_0Routeenum PageTypeinvalid discriminant for PageTypemissing discriminant for PageTypeAppPagetuple struct AppPagePathSegmentvariant index 0 <= i < 4AppPathtuple struct AppPathNextServerToClientTransitionssrstruct NextServerToClientTransitionpackages/next-swc/crates/next-core/src/next_client_component/server_to_client_transition.rs<NextServerToClientTransition as turbo_tasks :: debug :: ValueDebug>::dbg<NextServerToClientTransition as turbo_tasks :: debug :: ValueDebug>::dbg_depthprocess<NextServerToClientTransition as Transition>::processCssClientReferenceModuleclient_modulestruct CssClientReferenceModulepackages/next-swc/crates/next-core/src/next_client_reference/css_client_reference/css_client_reference_module.rs<CssClientReferenceModule as turbo_tasks :: debug :: ValueDebug>::dbg<CssClientReferenceModule as turbo_tasks :: debug :: ValueDebug>::dbg_depthCssClientReferenceModule::newcss client referencecss_client_reference_modifierident<CssClientReferenceModule as Module>::identcontent<CssClientReferenceModule as Asset>::contentCssClientReferenceModule has no contentparse_css<CssClientReferenceModule as ParseCss>::parse_cssNextEcmascriptClientReferenceTransitionclient_transitionssr_transitionstruct NextEcmascriptClientReferenceTransitionpackages/next-swc/crates/next-core/src/next_client_reference/ecmascript_client_reference/ecmascript_client_reference_transition.rs<NextEcmascriptClientReferenceTransition as turbo_tasks :: debug :: ValueDebug>::dbg<NextEcmascriptClientReferenceTransition as turbo_tasks :: debug :: ValueDebug>::dbg_depthNextEcmascriptClientReferenceTransition::new<NextEcmascriptClientReferenceTransition as Transition>::processNextDynamicTransitionstruct NextDynamicTransitionpackages/next-swc/crates/next-core/src/next_dynamic/dynamic_transition.rs<NextDynamicTransition as turbo_tasks :: debug :: ValueDebug>::dbg<NextDynamicTransition as turbo_tasks :: debug :: ValueDebug>::dbg_depthNextDynamicTransition::new<NextDynamicTransition as Transition>::processClientReferenceManifest::build_outputcssPathRegexregexnamed_paramsNamedParamstruct NamedParamSingleMultiNamedParamKindenum NamedParamKindnode_modules/