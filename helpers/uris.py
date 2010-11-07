import math

def FirstUri(Page,PageSize,Count,Path):
	return Path+'?PageSize='+str(PageSize)+'&Page=0'

def LastUri(Page,PageSize,Count,Path):
	LastPage = math.ceil(float(Count)/PageSize)-1
	return Path+'?PageSize='+str(PageSize)+'&Page='+str(LastPage)
	
def NextUri(Page,PageSize,Count,Path):
	if ((Page*PageSize)+PageSize) < Count:
		return Path+'?PageSize='+str(PageSize)+'&Page='+str(Page+1)
	else:
		return ""
	
def PrevUri(Page,PageSize,Count,Path):
	if Page == 0:
		return ""
	else:
		return Path+'?PageSize='+str(PageSize)+'&Page='+str(Page-1)
	
def CurUri(Path,QueryString):
	return Path+'?'+QueryString