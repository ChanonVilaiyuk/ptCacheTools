from tools import getInfo
reload(getInfo)

from tools import info
reload(info)

project = str()
episode = str()
sequence = str()
shot = str()
projectCode = str()
episodeCode = str()
cacheRawPath = str()
cachePath = str()
backupCache = str()
logPath = str()
dbPath = str()
heroCachePath = str()
referenceDBPath = str()
logPath = str()


def setPathInfo() : 
	try : 
		currentLevel = getInfo.ptPipelineSceneInfo('animFilePath')
		project = getInfo.ptPipelineSceneInfo('project')
		episode = getInfo.ptPipelineSceneInfo('episode')
		sequence = getInfo.ptPipelineSceneInfo('sequence')
		shot = getInfo.ptPipelineSceneInfo('shot')

		projectInfo = info.project(project)
		projectCode = projectInfo.code()
		episodeInfo = info.episode(project, episode)
		episodeCode = episodeInfo.code()

		dbFile = '%s_%s_%s_%s_assetCache.txt' % (projectCode, episodeCode, sequence, shot)
		heroCacheFile = '%s_%s_%s_%s_heroCache.txt' % (projectCode, episodeCode, sequence, shot)
		referenceDBFile = '%s_%s_%s_%s_referenceDB.txt' % (projectCode, episodeCode, sequence, shot)


		dbPath = os.path.join(currentLevel, 'cache', 'data', dbFile)
		heroCachePath = os.path.join(currentLevel, 'cache', 'data', heroCacheFile)
		referenceDBPath = os.path.join(currentLevel, 'cache', 'data', referenceDBFile)
		logPath = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'log'), '/')


		cacheRawPath = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'raw'), '/')
		cachePath = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'hero'), '/')
		backupCache = mayaTools.fixPath(os.path.join(currentLevel, 'cache', 'backup'), '/')


		return True

	except : 
		return False


def info() : 
	tmpData = {
				'project': project, 
				'episode': episode, 
				'sequence': sequence, 
				'shot': shot, 
				'projectCode': projectCode, 
				'episodeCode': episodeCode, 
				'cachePath': cacheRawPath, 
				'heroCachePath': cachePath, 
				'backupCachePath': backupCache, 
				'logPath': logPath
	}

	return tmpData