def func(h,arr):
    if(h.left!=None):
        arr= func(h.left,arr)
    if(h.right!=None):
        arr= func(h.right,arr)
    if h.left!=None & h.right is not None:
        arr.append(h.data)
    return arr


arr=[]
if root!=None:
    temp=root
    while(temp!=None):
        arr.append(temp.data)
        temp= temp.left
    if root.left!=None:
        arr.pop(len(arr)-1)
    temp= root
    arr= func(temp,arr)
return arr