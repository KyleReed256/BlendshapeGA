import maya
import maya.cmds as cmds
import os
import sys
import numpy as np
import glob
import maya.mel as mel
import scipy.io as spio
from functools import partial
import itertools
import random

global BlendshapeWeightMatrix
global startingID
global randomTargetList



def setupBlendshapes(FACE_ID,envName,tIDs,oN,*args):

	global numVerts
	global identityMesh
	global smileScores
	global avgSmileVec
	global matData
	global eigenvalues
	global components
	global W
	global v
	global SAMPLE_RANGE
	global SmileLog
	global startingID
	global owd
	global testIDs
	global numPCs
	global outName
	global SmileChosenLog
	global generation
	global num_Bs

	testIDs = tIDs
	owd = envName
	os.chdir(owd)
	startingID = testIDs[FACE_ID-1]
	SAMPLE_RANGE = 0.05
	pcNum = 25
	outName = oN
	SmileLog = []
	SmileChosenLog = []
	numVerts = 4906
	generation = 0

	filePath = "Resources/PPCA_smile.mat"
	matData = spio.loadmat(filePath)

	avgSmileVec = matData['mu']
	avgSmileVec = avgSmileVec[0]

	smileScores = [None] * 18
	gen = 0
	outName = oN
	# neutral_Filename = "neutrals/FACE"+str(FACE_ID)+"_Neutral.obj"
	# neutral_Filename = "neutrals/bathFemale000.obj"
	neutral_Filenames = glob.glob("Dataset/OBJs_neutrals/*.obj")
	neutral_Filename = neutral_Filenames[startingID-1]
	print neutral_Filename
	cmds.file(neutral_Filename,i=True,groupName="blendshapes")
	cmds.select('Mesh')
	mel.eval('polySetToFaceNormal')
	moveFaceVertices('Mesh',avgSmileVec)


	os.chdir("Blendshapes/smile/smilePop/TEST"+str(startingID)+'/')
	obj_Filenames = glob.glob("*.obj")
	num_Bs = len(obj_Filenames)

	for i in range(num_Bs):
		bsN = 'BLENDSHAPE'+str(i+1)
		cmds.scriptEditorInfo(suppressWarnings=True)
		filePath = obj_Filenames[i]
		filePathWtExt = filePath.rsplit('.', 1)[0]
		print 'Loading Mesh file: ' + filePath
		faceObj = cmds.file(filePath,i=True, rnn=True, ignoreVersion = True, options = "mo=0",  loadReferenceDepth  = "all")
		print faceObj[4]
		cmds.rename(faceObj[4], bsN)
		cmds.select(bsN)
		mel.eval('polySetToFaceNormal')
		cmds.move(500 + 200*((i)%10),-300.0*((i)/10),0,r=True)

	cmds.group('BLENDSHAPE*',n='blendshapes',w=True)
	# cmds.select('faces',all=True)

	## Pressing Blendshape button
	mel.eval('select -r "BLENDSHAPE*"')
	mel.eval('select -tgl "Mesh"')
	mel.eval('blendShape;')



def useIDsBlendShapeWeights(inputID,bsID,startingID,*args):

	bSLog = []
	for bs in range(1,Num_BlendShapes+1):
		bsName = 'blendShape' +str(inputID)+ '.' + 'FACE' + str(startingID) + '_' + BlendshapeNames[bs-1] + '_Mesh'
		bsWeight = BlendshapeWeightMatrix[bsID-1,bs-1]
		# print bsName
		# print bsWeight
		#mel.eval('setAttr "blendShape1.FACE1_DUAL_smile_CTL_Mesh" 0.405634')
		scriptName = "setAttr" + " \"" + bsName + "\" " + str(bsWeight) + ";"
		# scriptName2 = "setAttr" + " \"" + "Mesh." + bsName + "\" " + str(bsWeight) + ";"
		# print scriptName
		# mel.eval(scriptName)
		# mel.eval('setAttr "blendShape1.FACE1_DUAL_smile_CTL_Mesh" 0.405634')
		cmds.setAttr(bsName,bsWeight)

def create18Faces(startID,*args):
	global startingID
	global numPCs
	global generation
	global randomTargetList

	randomTargetList = setUpRandomTarget()
	print randomTargetList

	for face in range(1,19):
		cmds.select('Mesh')
		faceN = 'face'+str(face)
		cmds.duplicate('Mesh',n=faceN)
		mel.eval('select -r "BLENDSHAPE*"')
		mel.eval('select -tgl '+faceN)
		mel.eval('blendShape;')

		addRandomSmile(face)
		print 'Face ' + str(face) + ' spawned at random'

		
		cmds.select('face'+str(face))
		cmds.move(200*((face-1)%6),1200 + (-300.0*((face-1)/6)),0,r=True)
	cmds.group('face*',n='faces',w=True)
	cmds.select('faces')
	cmds.viewFit()

	# createGeneUI()

def addRandomSmile(faceID,*args):
	global randomTargetList
	global identityMesh
	global smileScores
	global startingID


	try:
		randomSmile = randomTargetList[0]
	except IndexError:
		print 'WARNING'
		randomTargetList = setUpRandomTarget()
		randomSmile = randomTargetList[0]


	print 'Random smile chosen as:' + str(randomTargetList[0]+1)
	smileOut = np.zeros(num_Bs)
	smileOut[randomSmile] = 1.0
	smileScores[faceID-1] = smileOut
	setBlendShapePCs(faceID,smileOut,startingID)
	randomTargetList = np.delete(randomTargetList,0)


def createGeneUI(*args):
	global startingID
	print startingID
	myWindow = "Smile Selector"
	if maya.cmds.window(myWindow,ex=True):
		maya.cmds.deleteUI(myWindow)
	cmds.window(myWindow, width = 300, height = 200) 
	cmds.columnLayout("columnLayoutName01", adjustableColumn=True )
	cmds.text("3DFITtitle", label = "Check boxes of most similar faces:", width = 20, height = 20, backgroundColor = [0.2, 0.2, 0.2])
	cmds.gridLayout( numberOfColumns=6, nr = 3, cellWidthHeight=(50, 50),parent = "columnLayoutName01" )
	cBox = []
	for cB in range(18):
		cBox.append(cmds.checkBox( label = str(cB+1) ,align='right'))
		#cBvals[cB-1] = cmds.checkBox(cBox, query = True, value = True)
	cmds.separator(parent = "columnLayoutName01")
	cmds. rowLayout("nameRowLayout01", numberOfColumns = 2, parent = "columnLayoutName01")
	cmds.text( label = "Select ID of MOST similar face:", width = 200, height = 20, backgroundColor = [0.2, 0.2, 0.2],parent = "nameRowLayout01")
	bestFace = cmds.intField( "bestFace", minValue = 1, maxValue = 18, value = 18,editable=True, parent = "nameRowLayout01")
	cmds.separator(parent = "columnLayoutName01")
	cmds.button(label = "Next Generation", command = partial(generateNextGen,bestFace,cBox,True),parent = "columnLayoutName01")
	cmds.button(label = "Save Face", command = partial(saveFace,bestFace),parent = "columnLayoutName01")
	cmds.showWindow()

def generateNextGen(bF,cBvals,interFaceCond,*args):

	global identityMesh
	global smileScores
	global SmileLog
	global SmileChosenLog
	global num_Bs
	global generation
	global FaceBSLog

	generation += 1

	oldSmileScores = smileScores[:]

	chosenFaces = []
	if(interFaceCond==True):
		for cB in range(18):
			if cmds.checkBox( cBvals[cB],q=True, v=True):
				chosenFaces.append(cB+1)

		bestFace = `cmds.intField( bF, query = True, value = True)`
	else:
		bestFace = str(bF)
		chosenFaces = cBvals

	chosenFaces2 = chosenFaces[:]

	if int(bestFace) in chosenFaces:
		chosenFaces2.remove(int(bestFace))
	print chosenFaces2

	chosenCombos = itertools.combinations(chosenFaces2, 2)
	chosenCombos = list(chosenCombos)

	chosenSmiles = []
	for j in range(len(chosenFaces2)):
		chosenSmiles.append(oldSmileScores[int(chosenFaces2[j])-1])
	eliteFaceScore = oldSmileScores[int(bestFace)-1]
	chosenSmiles.insert(0,eliteFaceScore)
	SmileChosenLog.append(chosenSmiles[:])

	for i in range(1,19):
		if i==1:
			eliteFaceScore = list(oldSmileScores[int(bestFace)-1])
			smileScores[i-1] = eliteFaceScore
			setBlendShapePCs(i,eliteFaceScore,startingID)
			print 'Face 1 chosen as ELITE face: '+ bestFace
			print eliteFaceScore
		elif i==2:
			eliteFaceScore = np.array(oldSmileScores[int(bestFace)-1])
			chosenSum = eliteFaceScore
			for t in range(len(chosenFaces2)):
				chosenSum += np.array(oldSmileScores[chosenFaces2[t]-1])
			avgFace = chosenSum / (len(chosenFaces2)+1)
			smileScores[i-1] = avgFace
			setBlendShapePCs(i,avgFace,startingID)
			
			print 'Face 2 chosen as average of: '+ bestFace + ' and ' + str(chosenFaces2)
			print avgFace

		elif i<(len(chosenFaces2)+len(chosenCombos)+3):
			if i < len(chosenFaces2)+3:
				f1 = bestFace
				f2 = chosenFaces2[i-3]
				print 'Face '+ str(i) +' chosen as average of ELITE and Face ' + str(f2)
			else:
				j = i - (len(chosenFaces2)+3)
				chosenTemp = chosenCombos[j]
				f1 = chosenTemp[0]
				f2 = chosenTemp[1]
				print 'Face '+ str(i) +' chosen as average of Face ' + str(f1) +' and Face ' + str(f2)
			f1PCs = np.array(oldSmileScores[int(f1)-1])
			f2PCs = np.array(oldSmileScores[int(f2)-1])
			meanPCs = (f1PCs + f2PCs) / 2
			print meanPCs
			smileScores[i-1] = meanPCs
			setBlendShapePCs(i,meanPCs,startingID)

		elif i<12:
			f1 = random.choice(chosenFaces)
			numChanges = 3
			chosenPCs = random.sample(range(num_Bs),numChanges)
			cFace = list(oldSmileScores[f1-1])
			# print 'cFace:'
			# print cFace
			ranFace = mutateBlendshapes(cFace,0.5,chosenPCs)
			smileScores[i-1] = ranFace
			setBlendShapePCs(i,ranFace,startingID)
			print 'Face '+ str(i) + ' chosen as mutation of Face ' + str(f1) +' for PC ' + str(chosenPCs) 
			print ranFace
		else:
			addRandomSmile(i)
			print 'Face ' + str(i) + ' spawned at random'

	smileScoresCopy = smileScores[:]
	SmileLog.append(smileScoresCopy)

	# global groundTruth
	# global smileBSdeltas
	# faceVec = blendshapesToVec(list(oldSmileScores[int(bestFace)-1]),smileBSdeltas)
	# print faceVec
	# res = np.array(groundTruth) - np.array(faceVec)
	# print res
	# sse = np.sqrt(np.sum(res**2))
	# print sse
	# sseList.append(sse)
	# print sseList


def getBlendShapePCs(faceID,startingID,*args):
	cFaceList = []
	for pc in range(num_Bs):
		bsName = 'blendShape' +str(faceID+1)+ '.' + 'BLENDSHAPE' + str(pc+1)
		cFaceList.append(cmds.getAttr( bsName))
	return cFaceList
    
def setBlendShapePCs(faceID,bshapeList,startingID,*args):
	for pc in range(len(bshapeList)):
		bsName = 'blendShape' +str(faceID+1)+ '.' + 'BLENDSHAPE' + str(pc+1)
		cmds.setAttr( bsName,bshapeList[pc])

def createFaceBSLog(*args):
	global startingID
	FaceBSLog = []
	for i in range(1,19):
		cFaceList = getBlendShapePCs(i,startingID)
		FaceBSLog.append(cFaceList)
	return FaceBSLog

def mutateBlendshapes(mutateFace,mutateRate,chosenPCs,*args):

	for i in range(len(chosenPCs)):
		mutateFace[chosenPCs[i]] = random.uniform(0,mutateRate)
	return mutateFace


def randBlendshapes(mutateFace,chosenPCs,*args):
	global Num_BlendShapes
	randWeights = []

	randBlends = np.zeros(Num_BlendShapes)
	
	#Smile blendshape

	randBlends[2] = random.uniform(0.5, 1)
	for i in range(len(chosenPCs)):
		randBlends[chosenPCs[i]] = random.uniform(0, mutateFace)

	return randBlends

def saveFace(bF,*args):
	global SmileLog
	global startingID
	global owd
	global smileScores
	global SmileChosenLog
	global outName

	os.chdir(owd + '/resultingLogs')
	bestFace = `cmds.intField( bF, query = True, value = True)`
	oldSmileScores = smileScores[:]
	eliteFaceScore = oldSmileScores[int(bestFace)-1]
	SmileChosenLog.append(eliteFaceScore)
	# eliteFace = getFaceVec(int(bestFace),'glob')
	# fileName = 'Composite_FACE' + str(startingID) + '_ppcaSmiles_' + bestFace + '.mat'
	# spio.savemat(fileName, {"eliteFace": eliteFace})
	# print 'Saved End Face: ' + fileName
	fileName2 = 'SmileLog_FACE' + str(startingID) + '_samplePopSmileBSv_' + str(outName) + '.mat'
	fileName3 = 'SmileChosenLog_FACE' + str(startingID) + '_samplePopSmileBSv_' + str(outName) + '.mat'
	spio.savemat(fileName2, {"SmileLog": SmileLog})
	spio.savemat(fileName3, {"SmileChosenLog": SmileChosenLog})
	print 'Saved Smile Log:' + fileName2
	print 'Saved Chosen Log:' + fileName3

	faceID = int(bestFace)
	cmds.select('face' + bestFace)
	cmds.move(-200*((faceID-1)%6),300.0*((faceID-1)/6),0,r=True)

	eliteFace = getFaceVec(int(bestFace),'glob')
	fileName = 'FACE' + str(startingID) + '_samplePopSmileBSv_' + outName + '.mat'
	spio.savemat(fileName, {"smileResult":eliteFace})

def setUpRandomTarget(*args):

	global num_Bs

	rTList = np.random.permutation(num_Bs)

	return rTList

def moveFaceVertices(faceName,newFaceVec,*args):

    global numVerts
    cFaceList = []
    for vert in range(numVerts):
        vertexName = faceName +'.vtx['+str(vert)+']'
        mel.eval('select -r ' + vertexName)
        newX = newFaceVec[3*vert]
        newY = newFaceVec[3*vert+1]
        newZ = newFaceVec[3*vert+2]
        #print xyz
        cmds.move(newX, newY, newZ ,relative=True)
    mel.eval('select -cl ')

def getFaceVec(meshName,locOrGlob,*args):
    global numVerts
    cFaceList = []
    for vert in range(numVerts):
        vertexName = meshName + '.vtx['+str(vert)+']'
        mel.eval('select -r ' + vertexName)
        if(locOrGlob == 'loc'):
        	xyz = cmds.pointPosition( vertexName , l=True)
    	else:
    		xyz = cmds.pointPosition( vertexName )
        cFaceList.append(xyz[0])
        cFaceList.append(xyz[1])
        cFaceList.append(xyz[2])
    mel.eval('select -cl ')
    return cFaceList

def getAllFaceVecs(locOrGlob,*args):
	global locNeutral
	FaceVecMatrix = []
	for face in range(1,19):
		cFaceList = getFaceVec('face'+str(face),locOrGlob)
		cFaceList = np.array(cFaceList) - np.array(locNeutral)
		FaceVecMatrix.append(cFaceList)
	return FaceVecMatrix

def automatedEvolution(NUM_GENERATIONS,*args):

	global FaceBSLog
	global nextBest
	global nextElite
	global smileScores
	global groundTruth
	global smileBSdeltas
	global sseList
	global owd
	global testIDs
	global startingID
	global avgSmileVec
	sseList = []

	SSE_gens = []

	os.chdir(owd)

	filePath = "Resources/smileDeltasFull.mat"
	matData = spio.loadmat(filePath)
	smileBSdeltas = matData['exprDeltas']
	groundTruth = smileBSdeltas[startingID-1]
	newIDs = [x - 1 for x in testIDs]
	smileBSdeltas = np.delete(smileBSdeltas,newIDs,0)

	for gen in range(NUM_GENERATIONS):

		genResults = compareWithGroundTruth(groundTruth,smileBSdeltas,smileScores)
		SSE_gens.append(genResults['smallestSSE'])

		nextElite = genResults['eliteIndex']
		nextBest = genResults['bestFaces']

		generateNextGen(nextElite,nextBest,False)


	print SSE_gens

	print 'Final SSE: ' + str(SSE_gens[-1])



def compareWithGroundTruth(groundTruth,smileBSdeltas,FaceMatrix,*args):

	global startingID
	

	sseList = []
	for face in range(1,19):
		faceBlendshapes = FaceMatrix[face-1]
		print 'Face Blendshape:' + str(face)
		print faceBlendshapes
		faceVec = blendshapesToVec(faceBlendshapes,smileBSdeltas)
		res = np.array(groundTruth) - np.array(faceVec)
		sse = np.sqrt(np.sum(res**2))
		sseList.append(sse)

	print sseList
	sortedSSE = np.argsort(sseList)
	smallestSSE = sseList[sortedSSE[0]]
	sortedSSE = [x+1 for x in sortedSSE]
	eliteIndex = sortedSSE[0]
	bestFaces = sortedSSE[:4]

	print 'Elite Face:' + str(eliteIndex)
	print 'Best Faces:' + str(bestFaces[:4])
	print 'Smallest SSE' + str(smallestSSE)

	return {'eliteIndex':eliteIndex, 'bestFaces':bestFaces ,'smallestSSE':smallestSSE }

def blendshapesToVec(blendshapes,neutralBSdeltas,*args):
	faceVec = np.matmul(blendshapes, neutralBSdeltas)

	return faceVec













