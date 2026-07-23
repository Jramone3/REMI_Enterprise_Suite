erence::ecmascript_client_reference::ecmascript_client_reference_module::EcmascriptClientReferenceProxyChunkItem::turbo_tasks :: debug :: ValueDebug::dbg_depthmetadata file not found: collect_direct_exportsnext-core@next_core::next_app::metadata::image::collect_direct_exportsdynamic_image_metadata_sourcenext-core@next_core::next_app::metadata::image::dynamic_image_metadata_source?twitteropenGraph${size.width}x${size.height}anydata.sizes = ``;data.width = size.width; data.height = size.height;./.import { 
import { fillMetadataSegment } from 'next/dist/lib/metadata/get-metadata-route'

const imageModule = {  }

export default async function (props) {
    const { __metadata_id__: _, ...params } = await props.params
    const imageUrl = fillMetadataSegment(, params, )

    const { generateImageMetadata } = imageModule

    function getImageMetadata(imageMetadata, idParam) {
        const data = {
            alt: imageMetadata.alt,
            type: imageMetadata.contentType || 'image/png',
            url: imageUrl + (idParam ? ('/' + idParam) : '') + ,
        }
        const { size } = imageMetadata
        if (size) {
            
        }
        return data
    }

    const imageMetadataArray = await generateImageMetadata({ params })
    return imageMetadataArray.map((imageMetadata, index) => {
        const idParam = imageMetadata.id + ''
        return getImageMetadata(imageMetadata, idParam)
    })
}
