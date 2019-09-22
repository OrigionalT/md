
class Student(object):

    def __init__(self,request):

        self._request = request
        self.__pri = 10

stu = Student('10')

print(stu.request)

