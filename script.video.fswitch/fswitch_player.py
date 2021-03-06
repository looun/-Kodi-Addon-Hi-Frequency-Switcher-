import os
import xbmc
import fswitch_message as fsmsg
import fswitch_util as fsutil
import fswitch_config as fsconfig

class fsPlayer(xbmc.Player):
    ' player subclass'
    
    def __init__(self):
        super(xbmc.Player, self).__init__()

    # onPlayBack action includes onResume
    def onPlayBackStarted(self):

        # only switch on video files (not audio)
        if not xbmc.Player().isPlayingAudio():
            fsconfig.lastPlayedMediaType = 'video'

            if fsconfig.radioOnPlayStart:

                # retry this up to 100 times - for slow DVD/BD/UHD ISO play-back (100 x 0.4s = 40 seconds max)
                for retryCounter in range(0, 100):

                    # set the output mode automatically
                    setModeStatus, statusType = fsutil.setDisplayModeAuto()
                  
                    # video not started - wait, then retry
                    if (setModeStatus == 'No playing video detected.'):
                        xbmc.sleep(400)

                    # video started - retry if FPS not yet found in log (note: wait 0.4s already in get source FPS function)
                    else:
                        if (setModeStatus != 'Failed to get source framerate.'):
                            break

                # display notification
                if statusType == 'warn':
                    fsmsg.notifyQuickWarn('Frequency Switcher', setModeStatus)    
                else:
                    fsmsg.notifyInfo('Frequency Switcher', setModeStatus)
    
        else:
            fsconfig.lastPlayedMediaType = 'audio'

    def onPlayBackEnded(self):
        self.onPlayBackEndedOrStopped()

    def onPlayBackStopped(self):
        self.onPlayBackEndedOrStopped()
        
    def onPlayBackEndedOrStopped(self):
    
        # only switch on video files (not audio)
        if fsconfig.lastPlayedMediaType == 'video':

            if fsconfig.radioOnPlayStop60 or fsconfig.radioOnPlayStop50 or fsconfig.radioOnPlayStop24 or fsconfig.radioOnPlayStop23:

                # check current display mode setting
                currentOutputMode, currentHiSiliconMode = fsutil.getDisplayMode()
                
                if currentOutputMode == 'unsupported':
                    setModeStatus = 'Unsupported resolution: ' + currentHiSiliconMode           
                    statusType = 'warn'
                        
                elif currentOutputMode == 'invalid':
                    setModeStatus = 'Error, unexpected mode: ' + currentHiSiliconMode       
                    statusType = 'warn'
                    
                else:
                    # get current resolution
                    resSplit = currentOutputMode.find('-')
                    currentRes = currentOutputMode[0:resSplit]
    
                    # set the output mode
                    if fsconfig.radioOnPlayStop60:
                        setModeStatus, statusType = fsutil.setDisplayMode(currentRes + '-60hz')
                    elif fsconfig.radioOnPlayStop50:
                        setModeStatus, statusType = fsutil.setDisplayMode(currentRes + '-50hz')
                    elif fsconfig.radioOnPlayStop24:
                        setModeStatus, statusType = fsutil.setDisplayMode(currentRes + '-24hz')
                    else:
                        setModeStatus, statusType = fsutil.setDisplayMode(currentRes + '-23hz')

                # display force 2D mode
                osPlatform, osVariant, osSDK = fsutil.getPlatformType()
                if osSDK == '24':
                    os.system('echo 0 > /sdcard/mode3D')
                os.system('echo 3dmode 0 > /proc/msp/hdmi0')
                
                # display notification
                if statusType == 'warn':
                    fsmsg.notifyQuickWarn('Frequency Switcher', setModeStatus)    
                else:
                    fsmsg.notifyInfo('Frequency Switcher', setModeStatus)
        
