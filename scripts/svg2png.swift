import AppKit
let args = CommandLine.arguments
let src = URL(fileURLWithPath: args[1]); let dst = URL(fileURLWithPath: args[2]); let W = Double(args[3])!
guard let img = NSImage(contentsOf: src) else { print("load fail"); exit(1) }
let s = img.size; let k = W / s.width; let Hh = (s.height * k).rounded()
let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: Int(W), pixelsHigh: Int(Hh), bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
img.draw(in: NSRect(x: 0, y: 0, width: W, height: Hh))
NSGraphicsContext.restoreGraphicsState()
try! rep.representation(using: .png, properties: [:])!.write(to: dst)
print("ok", Int(W), Int(Hh))
