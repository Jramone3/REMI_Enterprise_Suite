site_map_route_sourceimport { NextResponse } from 'next/server'
import * as _imageModule from 

const imageModule = { ..._imageModule }

const handler = imageModule.default
const generateImageMetadata = imageModule.generateImageMetadata

if (typeof handler !== 'function') {
    throw new Error('Default export is missing in ')
}

export async function GET(_, ctx) {
    const params = await ctx.params
    const { __metadata_id__, ...rest } = params || {}
    const restParams = params ? rest : undefined
    const targetId = __metadata_id__
    let id = undefined

    if (generateImageMetadata) {
        const imageMetadata = await generateImageMetadata({ params: restParams })
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

    return handler({ params: restParams, id })
}

export * from 