import Foundation
import Vision
import AppKit

guard CommandLine.arguments.count > 1 else {
    FileHandle.standardError.write("usage: img_ocr <image-path> [<image-path> ...]\n".data(using: .utf8)!)
    exit(1)
}

func ocr(_ path: String) {
    let url = URL(fileURLWithPath: path)
    guard let img = NSImage(contentsOf: url),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        print("[ERROR] cannot load \(path)")
        return
    }
    let request = VNRecognizeTextRequest { req, _ in
        let results = (req.results as? [VNRecognizedTextObservation]) ?? []
        // Sort by top-to-bottom (y descending means top first in Vision's normalized coords)
        let sorted = results.sorted { a, b in
            let ay = a.boundingBox.midY
            let by = b.boundingBox.midY
            if abs(ay - by) > 0.02 { return ay > by }
            return a.boundingBox.minX < b.boundingBox.minX
        }
        for obs in sorted {
            if let candidate = obs.topCandidates(1).first {
                let bb = obs.boundingBox
                // print with approx coords for reconstructing layout
                print("(x=\(String(format: "%.2f", bb.minX)) y=\(String(format: "%.2f", 1 - bb.midY))) \(candidate.string)")
            }
        }
    }
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    let langs = ["zh-Hans", "en-US"]
    if #available(macOS 13.0, *) {
        request.recognitionLanguages = langs
    }
    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    try? handler.perform([request])
}

for p in CommandLine.arguments.dropFirst() {
    print("=== \(p) ===")
    ocr(p)
}
