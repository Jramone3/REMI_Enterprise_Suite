      const { size } = imageMetadata
        if (size) {
            
        }
        return data
    }

    if (generateImageMetadata) {
        const imageMetadataArray = await generateImageMetadata({ params })
        return imageMetadataArray.map((imageMetadata, index) => {
            const idParam = (imageMetadata.id || index) + ''
            return getImageMetadata(imageMetadata, idParam)
        })
    } else {
        return [getImageMetadata(imageModule, '')]
    }
}
.--metadata.jsno-cache, no-storepublic, immutable, no-transform, max-age=31536000public, max-age=0, must-revalidateimport { NextResponse } from 'next/server'

const contentType = 
const cacheControl = 
const buffer = Buffer.from(, 'base64')

export function GET() {
    return new NextResponse(buffer, {
        headers: {
            'Content-Type': contentType,
            'Cache-Control': cacheControl,
        },
    })
}

export const dynamic = 'force-static'
            import { NextResponse } from 'next/server'
            import handler from 
            import { resolveRouteData } from
'next/dist/build/webpack/loaders/metadata/resolve-route-data'

            const contentType = 
            const cacheControl = 
            const fileType = 

            export async function GET() {
              const data = await handler()
              const content = resolveRouteData(data, fileType)

              return new NextResponse(content, {
                headers: {
                  'Content-Type': contentType,
                  'Cache-Control': cacheControl,
                },
              })
            }
        [__metadata_id__]export async function generateStaticParams() {
    const sitemaps = await generateSitemaps()
    const params = []

    for (const item of sitemaps) {
        params.push({ __metadata_id__: item.id.toString() + '.xml' })
    }
    return params
}
import { NextResponse } from 'next/server'
import * as _sitemapModule from 
import { resolveRouteData } from 'next/dist/build/webpack/loaders/metadata/resolve-route-data'

const sitemapModule = { ..._sitemapModule }
const handler = sitemapModule.default
const generateSitemaps = sitemapModule.generateSitemaps
const contentType = 
const fileType = 

export async function GET(_, ctx) {
    const { __metadata_id__ = [], ...params } = ctx.params || {}
    const targetId = __metadata_id__[0]
    let id = undefined
    const sitemaps = generateSitemaps ? await generateSitemaps() : null

    if (sitemaps) {
        id = sitemaps.find((item) => {
            if (process.env.NODE_ENV !== 'production') {
                if (item?.id == null) {
                    throw new Error('id property is required for every item returned from generateSitemaps')
                }
            }
            return item.id.toString() === targetId
        })?.id

        if (id == null) {
            return new NextResponse('Not Found', {
                status: 404,
            })
        }
    }

    const data = await handler({ id })
    const content = resolveRouteData(data, fileType)

    return new NextResponse(content, {
        headers: {
            'Content-Type': contentType,
            'Cache-Control': cacheControl,
        },
    })
}

import { NextResponse } from 'next/server'
import * as _imageModule from 

const imageModule = { ..._imageModule }

const handler = imageModule.default
const generateImageMetadata = imageModule.generateImageMetadata

export async function GET(_, ctx) {
    const { __metadata_id__ = [], ...params } = ctx.params || {}
    const targetId = __metadata_id__[0]
    let id = undefined
    const imageMetadata = generateImageMetadata ? await generateImageMetadata({ params }) : null

    if (imageMetadata) {
        id = imageMetadata.find((item) => {
            if (process.env.NODE_ENV !== 'production') {
                if (item?.id == null) {
                    throw new Error('id property is required for every item returned from generateImageMetadata')
                }
            }
            return item.id.toString() === targetId
        })?.id

        if (id == null) {
            return new NextResponse('Not Found', {
                status: 404,
            })
        }
    }

    return handler({ params: ctx.params ? params : undefined, id })
}
packages/next-swc/crates/next-core/src/next_build.rsnext/dist/compiled/packages/next-swc/crates/next-core/src/next_client/context.rs./build/client/bootstrap.ts_./build/client/app-bootstrap.tsnext/dist/client/app-next-dev-turbopack.jspackages/next-swc/crates/next-core/src/next_client/runtime_entry.rsruntime reference resolved to an asset () that cannot be evaluatedpackages/next-swc/crates/next-core/src/next_client/transition.rsentry/next-hydrate.tsxnot an ecmascript placeable modulepackages/next-swc/crates/next-core/src/next_client_component/server_to_client_transition.rsnext-client-chunksentry/app/server-to-client.tsxentry/app/server-to-client-ssr.tsxnext-ssr-client-modulenext-edge-ssr-client-modulepackages/next-swc/crates/next-core/src/next_client_component/ssr_client_module_transition.rspackages/next-swc/crates/next-core/src/next_client_component/with_chunking_context_scope_asset.rspackages/next-swc/crates/next-core/src/next_client_component/with_client_chunks.rsChunkingContext::with_layer should not return a different kind of chunking contextcss__turbopack_esm__({
    default: () => __turbopack_import__(),
    chunks: () => chunks,
});
const chunks = ;
local asset packages/next-swc/crates/next-core/src/next_client_reference/css_client_reference/css_client_reference_module.rsCSS client reference client module must be CSS parseablepackages/next-swc/crates/next-core/src/next_client_reference/css_client_reference/css_client_reference_module_type.rsclient asset is not CSS chunk placeablepackages/next-swc/crates/next-core/src/next_client_reference/ecmascript_client_reference/ecmascript_client_reference_module.rspackages/next-swc/crates/next-core/src/next_client_reference/ecmascript_client_reference/ecmascript_client_reference_proxy_module.rsimport { createProxy } from 'next/dist/build/webpack/loaders/next-flight-loader/module-proxy'

const proxy = createProxy()

// Accessing the __esModule property and exporting $$typeof are required here.
// The __esModule getter forces the proxy target to create the default export
// and the $$typeof value is for rendering logic to determine if the module
// is a client boundary.
const { __esModule, $$typeof } = proxy;

export { __esModule, $$typeof };
export default proxy;
proxy asset is not an ecmascript moduleEcmascriptModuleAsset must implement EcmascriptChunkItemchunking context must impl EcmascriptChunkingContext to use EcmascriptClientReferenceProxyModulepackages/next-swc/crates/next-core/src/next_client_reference/ecmascript_client_reference/ecmascript_client_reference_transition.rsnext/dist/esm/next/dist/client asset is not ecmascript chunk placeableSSR asset is not ecmascript chunk placeablepackages/next-swc/crates/next-core/src/next_client_reference/visit_client_reference.rspackages/next-swc/crates/next-core/src/next_config.rs/_next/Loading Next.js confignext/entry/config/next.jsnext_configEvaluation of Next.js config failedexperimental.turbo.loadersexperimental.turbo.rulesThe new option is similar, but the key should be a glob instead of an extension.
Example: loaders: { ".mdx": ["mdx-loader"] } -> rules: { "*.mdx": ["mdx-loader"] }packages/next-swc/crates/next-core/src/next_dynamic/dynamic_module.rsdynamic client asset must be chunkablepackages/next-swc/crates/next-core/src/next_dynamic/dynamic_transition.rspackages/next-swc/crates/next-core/src/next_dynamic/visit_dynamic.rspackages/next-swc/crates/next-core/src/next_edge/context.rsnext/dist/compiled/buffernext/dist/build/polyfills/processimport * as module from "MODULE"

self._ENTRIES ||= {}
self._ENTRIES[] = module
packages/next-swc/crates/next-core/src/next_edge/entry.rspackages/next-swc/crates/next-core/src/next_edge/page_transition.rsentry/app/hydrate.tsxInternal module is not chunkablenext/dist/shared/lib/app-dynamicnext/dist/esm/shared/lib/dynamicpackages/next-swc/crates/next-core/src/next_edge/route_transition.rspackages/next-swc/crates/next-core/src/next_font/font_fallback.rspackages/next-swc/crates/next-core/src/next_font/google/font_fallback.rsdist/server/capsize-font-metrics.jsonFailed to find font override values for font ``Skipping generating a fallback font.packages/next-swc/crates/next-core/src/next_font/google/options.rspackages/next-swc/crates/next-core/src/next_font/google/stylesheet.rsinternal/font/google.jsimport cssModule from "@vercel/turbopack-next/internal/font/google/cssmodule.module.css?";
const fontData = {
    className: cssModule.className,
    style: {
        fontFamily: "",
        
    },
};

if (cssModule.variable != null) {
    fontData.variable = cssModule.variable;
}

export default fontData;
fontWeight: ,
fontStyle: "",
.module.cssNEXT_FONT_GOOGLE_MOCKED_RESPONSESdist/compiled/@next/font/dist/google/font-data.jsonfont-family: '';https://fonts.googleapis.com/css2'Expected one entrynext/font/google queries must have exactly one entrypackages/next-swc/crates/next-core/src/next_font/issue.rspackages/next-swc/crates/next-core/src/next_font/local/options.rspackages/next-swc/crates/next-core/src/next_font/local/stylesheet.rs@font-face {
    font-family: '';
    src: url('') format('');
    font-display: ;
    
}
font-weight: font-style: packages/next-swc/crates/next-core/src/next_font/local/util.rspackages/next-swc/crates/next-core/src/next_font/local/mod.rsimport cssModule from "@vercel/turbopack-next/internal/font/local/cssmodule.module.css?
    },
};

if (cssModule.variable != null) {
    fontData.variable = cssModule.variable;
}

export default fontData;
        next/font/local queries have exactly one entrypackages/next-swc/crates/next-core/src/next_font/stylesheet.rsascent-override: %;
descent-override: %;
line-gap-override: %;
';
    src: local(".className {
    font-family: : packages/next-swc/crates/next-core/src/next_font/util.rs_Fallback__packages/next-swc/crates/next-core/src/next_image/content_source.rswqinvalid w query argumentmissing w query argumentinvalid q query argumentmissing q query argumentmissing urlmissing querypackages/next-swc/crates/next-core/src/next_image/module.rspackages/next-swc/crates/next-core/src/next_image/source_asset.rsimport src from "IMAGE";
Input source is not a file and can't be transformed into image informationexport default { src, width: , height: , blurDataURL: `/_next/image?w=&q=&url=${encodeURIComponent(src)}`, blurWidth: , blurHeight:  }
, blurDataURL: , blurWidth: browser-experimental/*react/react-dom/react-server-dom-turbopack/*react-server-dom-webpack/next/dist/compiled/react-server-dom-turbopackreact-server-dom-turbopack/next/dist/client/components/noop-headnext/headnext/dynamicnode:next/dist/server/require-hooknext/dist/build/utilsnext/dist/build/webpack/loaders/next-flight-loader/action-proxyprivate-next-rsc-action-proxynext/dist/build/webpack/loaders/next-flight-loader/action-client-wrapperprivate-next-rsc-action-client-wrappernext/dist/build/webpack/loaders/next-flight-loader/action-validate/clientreact-server-dom-webpack/clientreact-server-dom-turbopack/client/client.edge/server.edge/server.nodenext/dist/esm/build/*next/dist/client/next/dist/esm/client/*next/dist/shared/next/dist/esm/shared/*next/dist/esm/pages/*next/dist/lib/next/dist/esm/lib/*next/dist/server/next/dist/esm/server/*next/dist/esm/pages/_appnext/dist/esm/pages/_documentnext/dist/esm/shared/lib/headnext/headersnext/dist/esm/client/components/headersnext/imagenext/dist/esm/shared/lib/image-externalnext/linknext/dist/esm/client/linknext/navigationnext/dist/esm/client/components/navigationnext/routernext/dist/esm/client/routernext/scriptnext/dist/esm/client/scriptnext/servernext/dist/esm/server/web/exports/indexnext/dist/client/components/headersnext/dist/client/components/navigationnext/dist/client/linknext/dist/client/routernext/dist/client/scriptnext/dist/pages/_appnext/dist/pages/_documentnext/dist/shared/lib/dynamicnext/dist/shared/lib/headnext/dist/shared/lib/image-externalnext/package.jsonNext.js package not foundpackages/next-swc/crates/next-core/src/next_manifests/client_reference_manifest.rsserver/app/_client-reference-manifest.jsglobalThis.__RSC_MANIFEST = globalThis.__RSC_MANIFEST || {};
globalThis.__RSC_MANIFEST[client reference chunks not foundpackages/next-swc/crates/next-core/src/next_pages/page_entry.rspages-api.jspages-edge-api.jsVAR_MODULE_DOCUMENT@vercel/turbopack-next/pages/_documentVAR_MODULE_APP@vercel/turbopack-next/pages/_appInvalid path type/src/instrumentationexport const register = hoist(userland, "register")
packages/next-swc/crates/next-core/src/next_route_matcher/mod.rspackages/next-swc/crates/next-core/src/next_server/context.rsdist/lib/server-external-packages.jsonpackages/next-swc/crates/next-core/src/next_server/resolve.rscjsjsmodule**/node_modules/{,packages/next-swc/crates/next-core/src/next_server/route_transition.rspackages/next-swc/crates/next-core/src/next_server_component/server_component_module.rschunking context must impl EcmascriptChunkingContext to use NextServerComponentModule),
});
packages/next-swc/crates/next-core/src/next_server_component/server_component_reference.rsNext.js server component packages/next-swc/crates/next-core/src/next_server_component/server_component_transition.rsnot an ecmascript modulepackages/next-swc/crates/next-core/src/next_shared/resolve.rsnext/dist/esm/.shared-runtimenext/dist/server/future/route-modules//vendored/contexts/app-routeunknownpackages/next-swc/crates/next-core/src/next_shared/transforms/emotion.rspackages/next-swc/crates/next-core/src/next_shared/transforms/relay.rspackages/next-swc/crates/next-core/src/next_shared/transforms/styled_components.rspackages/next-swc/crates/next-core/src/next_shared/transforms/styled_jsx.rspackages/next-swc/crates/next-core/src/next_telemetry.rsconst PAGE_PATH = ;

packages/next-swc/crates/next-core/src/page_loader.rsentry/page-loader.tsrequired file `entry/page-loader.ts` not foundstatic/chunks/pages__turbopack_load_page_chunks__()
packages/next-swc/crates/next-core/src/pages_structure.rs_document_errorentry/pages/_app.tsxentry/pages/_document.tsxentry/pages/_error.tsxindexpackages/next-swc/crates/next-core/src/sass.rssass_options must be an object*.module.scss*.module.sass*.scss*.sassnext/dist/compiled/sass-loadercompilerOptionsuseDefineForClassFieldsexperimentalDecoratorsemitDecoratorMetadatajsxImportSourceserver_path () is not in server_root ()The exported config object must contain an variable initializer.configExpected file content for file