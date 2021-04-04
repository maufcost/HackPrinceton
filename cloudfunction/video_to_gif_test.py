from GrabzIt import GrabzItAnimationOptions
from GrabzIt import GrabzItClient

grabzIt = GrabzItClient.GrabzItClient("YzVjNjVkMGE3MTlmNDdjOGIzNTU5MmFjMDgwMThjMzY=", "XD8/Pzg/P2guP0Y/CD9bAjw/Pz9/Pz96Jj8/P18YPT8=")

options = GrabzItAnimationOptions.GrabzItAnimationOptions()
options.framesPerSecond = 10
options.duration = 3
options.start = 0
options.width = 640
options.height = 360

grabzIt.URLToAnimation("https://storage.googleapis.com/vortexvideo/video.mp4", options)
# Then call the Save or SaveTo method
grabzIt.SaveTo("result.gif")
