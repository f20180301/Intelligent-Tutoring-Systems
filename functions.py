import sympy
import re
import random
import pickle
import datetime
from statistics import mean
from copy import deepcopy

students = dict()

question_template={
    "num_vars":None,
    "socialValue":None,
    "questionString":None,
    #//"placeHolderCategory":None,
    #fruits,places 
    "nameplaceHolderList":None,
    #"Ram bought (4)_ (Banana)_ in Market"
    #[starting index of Banana]
    "valueplaceHolderList":None,
    "equationList":None,
    "valueBasedQ":None,
    "optionsList":None,
    "correctOptionString":None

}


IDEAL_STEPS_SINGLE_VAR = 3
IDEAL_STEPS_DOUBLE_VAR = 11

questions = {
             "math_level_1":{
        "value_level_1":[
                         {
    "num_vars":1,
    "questionString": "Ram recently visited his aunt's place in Mumbai during the monsoon season. He observed a lot of water can be conserved using Rainwater Harvesting. Mumbai receives on an average 5 litres/ day of rainfall.How many days will it take to fill a hundred Litre water tank which is already having 15 litres water stored.",
    "nameplaceHolderList":["x"],
    "valueplaceHolderList":["Days"],
    "equationList": ["5 * x + 15 = 100"],
    "valueBasedQ":"Which among the following can help to reduce domestic water wastage?",
    "optionsList":["Closing and reparing the leaking taps", "Not having a bath regularly", "Using shower instaed of buckets", "Using sprinklers to water plants"],
    "correctOptionString": ["A", "D"]}
        ],
        "value_level_2":[
                         {
    "num_vars":1,
    "questionString": "A typical farm land yields Rs. 10000 worth crops. To harvest a farm manually, it generates 5500, while machines if used, requires only 2 days to do the job. How much should be the cost of the Machine per day to not compromise the profit as earned through manual labour? ",
    "nameplaceHolderList":["x"],
    "valueplaceHolderList":["Profit from Machines"],
    "equationList": ["10000 - 2 * x = 5500"],
    "valueBasedQ":"If the use of machines help reduce time and increase profitability, can all human labour be replaced by machines?",
    "optionsList":["Yes, always", "No, the value of skilled labours are appreciated in various filed and several machine operations are dependent on human skills", "Maybe", "Can't say much"],
    "correctOptionString": ["B"]}
        ]
        
    },
    "math_level_2":{
        "value_level_1":[
    {
    "num_vars":2,
    "questionString": "Ram is Enjoying Diwali at his home in Delhi. He wants to calculate how much Pollution it will cause to environment. He knows that burning 3 Non-Green Anar Bombs and 2 Green Chakris releases 300 mg of CO in air. And 5 Green Chakris releases 80 mg of CO in air. How much CO does burning of one Non-Green Anar Bomb or Green Chakri release in air?",
    "nameplaceHolderList":["x", "y"],
    "valueplaceHolderList":["Non-Green Anar Bombs", "Green Chakris"],
    "equationList": ["3 * x + 2 * y = 300", "5 * y = 80"],
    "valueBasedQ":"Do bursting fire crackers damage the environment, and which fire crackers are more environmental friendly?",
    "optionsList":["No, Green", "Yes, Green", "No, Non-green", "Yes, Non-green"],
    "correctOptionString": ["B"]},
    {
    "num_vars":2,
    "questionString": "Simran's father acts as a village worker. Even though he works really hard, he barely earns enough to feed his family and suffice daily needs. His neighbour, however did a government skill upliftment course and works in a agro based plant. The sum of their daily wages is Rs. 5000 and the difference is Rs. 2000. What are their wages?",
    "nameplaceHolderList":["x", "y"],
    "valueplaceHolderList":["Neighbor's Wage", "Father's Wage"],
    "equationList": ["x + y = 5000", "x - y = 2000"],
    "valueBasedQ":"Do you think that learning new skills and keeping one-self updated help increase one's income?",
    "optionsList":["No", "Yes", "Can't say anything", "Maybe"],
    "correctOptionString": ["B"]},
    ],
        "value_level_2":[
                         {
    "num_vars":2,
    "questionString": "Ram recently visited river Yamuna in Delhi. He saw streams of sewage flowing into the riverbeds and the water looking pale greenish at sites. He planned to calculate how much Pollution it will cause to environment. He knows that 3 power factory outlets and 2 household sewers releases 140 amount of toxins at a time.And 5 power factory and 2 household sewers releases 220 amount of toxins at a time.How much is the contributions of each power factory and households.", 
    "nameplaceHolderList":["x", "y"],
    "valueplaceHolderList":["Power Factory", "Household Sewers"],
    "equationList": ["3 * x + 2 * y = 140", "5 * x + 2 *y= 220"],
    "valueBasedQ":"How do you think the river pollution caused by factories and households can be dealt with?",
    "optionsList":["Filtration of sewer water before discharge", "Discharging the sewers directly to the seas", "Filtering the water at source of sewer generation", "Cleaning of rivers regularly"],
    "correctOptionString": ["A", "C", "D"]},
        ]
    }
             
    }





########################-- SINGLE VARIABLE HELPER EQUATIONS  --#####################################


def find_coefficient(eq1,eq2,choice='x'): #Returns the numbers to which each of the Equations should be multiplied inorder to eliminate x variable
  x1,y1,r1,x2,y2,r2= giveCoeffdouble(eq1,eq2)
  if choice == 'x':
    LCM=compute_lcm(x1,x2)
    t1=LCM/x1
    t2=LCM/x2
  else:
    LCM=compute_lcm(y1,y2)
    t1=LCM/y1
    t2=LCM/y2
  return t1,t2



def solveonevar(equation,var_sym='x'):  #Returns the answer of any Single Variable Equation
	
	# replacing all the x terms with j
	# the imaginary part
	s1 = equation.replace(var_sym, 'j')
	
	# shifting the equal sign to start
	# an opening bracket
	s2 = s1.replace('=', '-(')
	
	# adding the closing bracket to form
	# a complete expression
	s = s2+')'
	
	# mapping the literal j to the complex j
	z = eval(s, {'j': 1j})
	real, imag = z.real, -z.imag
	
	# if the imaginary part is true return the
	# answer
	# if imag:
	return (real/imag)
	# else:
	# 	if real:
	# 		return "No solution"
	# 	else:
	# 		return "Infinite solutions"


def evaluate(prev_eq, current_eq,var_sym='x'):  #Evaluates whether the Current Step is Consistent with the Previous Step
  correctStep = False
  idealStep = False
  current_eq = ''.join(current_eq.split())
  prev_eq = ''.join(prev_eq.split())
  if solveonevar(current_eq,var_sym) == solveonevar(prev_eq,var_sym):
    correctStep = True
  
  num2 = calcConsVars(current_eq,var_sym)
  num1 = calcConsVars(prev_eq,var_sym)

  if num2[0] <= num1[0] and num2[1] <= num1[1]:
    idealStep = True
  
  if (num2[0] == 1) and (num2[1] == 1 or current_eq.split('=')[1] == "0") and (current_eq.split('=')[0] == var_sym[0]):
    print("You are correct", "Yeahhh! we have reached the solution.")
    return 2 #Reached


  if not correctStep:
    print ("You are wrong", "Come on! Keep Trying.")
    return 0 #Bad
  
  print ("You are correct", "You are unnecessarily splitting the constants" if num2[0] > num1[0] else ("You are unnecessarily splitting the variables" if num2[1] > num2[1] else "Keep Going, You are doing GREAT!"))
  return 1 #Cool


def giveCoeff(currStep,var_sym='x'):  #returns the coefficients of a Single one Varable Linear Equation
  if var_sym=='y':
    y=sympy.Symbol(var_sym)
    left, right = currStep.split('=')
    exp_left=eval(left)
    exp_right=eval(right)
    # print(exp_left)
    # print(exp_right)
    # print(type(exp_left))
    # print(type(exp_right))

    if 'sympy' not in str(type(exp_right)):
      cr=exp_right
      cxr=0
    else:
      cxr=exp_right.coeff(y,1)
      cr=exp_right.coeff(y,0)
    if 'sympy' not in str(type(exp_left)):
      cl=exp_left
      cxl=0
    else:
      cxl=exp_left.coeff(y,1)
      cl=exp_left.coeff(y,0)
    
    # print(f"Coeff of x in LHS - {cxl}")
    # print(f"Coeff of x in RHS - {cxr}")
    # print(f"Constant in LHS - {cl}")
    # print(f"Constant in RHS - {cr}")
    return cxl,cxr,cl,cr
  else:
    x=sympy.Symbol(var_sym)
    left, right = currStep.split('=')
    exp_left=eval(left)
    exp_right=eval(right)
    # print(exp_left)
    # print(exp_right)
    # print(type(exp_left))
    # print(type(exp_right))

    if 'sympy' not in str(type(exp_right)):
      cr=exp_right
      cxr=0
    else:
      cxr=exp_right.coeff(x,1)
      cr=exp_right.coeff(x,0)
    if 'sympy' not in str(type(exp_left)):
      cl=exp_left
      cxl=0
    else:
      cxl=exp_left.coeff(x,1)
      cl=exp_left.coeff(x,0)
    
    # print(f"Coeff of x in LHS - {cxl}")
    # print(f"Coeff of x in RHS - {cxr}")
    # print(f"Constant in LHS - {cl}")
    # print(f"Constant in RHS - {cr}")
    return cxl,cxr,cl,cr


def givehint(problem_equation,var_sym='x',toprint=True):  #Gives Hint as to What to do next while Solving a One Variable Linear Order Equation, Also returns in which next step we should go.
  cxl,cxr,cl,cr=giveCoeff(problem_equation,var_sym)
  curstep=-1
  if cl!=0:
    if(toprint):
      print("Move Constant from LHS to RHS")
    curstep=0
  elif cxr!=0:
    if(toprint):
      print("Move the Variable Term from RHS to LHS")
    curstep=1
  else:
    if(toprint):
      print("Divide the Constant Term from the Coefficient of Variable")
    curstep=2
  return curstep

def solver_step_wise(problem_equation,var_sym='x',toprint=True):  # Solves the Single Variable in Step-Wise Format, and Returns the Final Answer 
  if(toprint):
    print("Initial Equation:  ", problem_equation)  #0
  [lhs,rhs]=problem_equation.split('=')
  prev_step=problem_equation
  step_num=givehint(prev_step,var_sym,False)

  if step_num==0:
    #moving cont from lhs to rhs --> cl=0
    cxl,cxr,cl,cr=giveCoeff(prev_step,var_sym)
    st1=""
    st1+=str(cxl)+"*"+var_sym
    st1+="="
    st1+=str(cxr)+"*"+var_sym
    if cr-cl>0:
      st1+="+"
    st1+=str(float(cr-cl))
    prev_step=st1
    if(toprint):
      print("Next Step:  ",prev_step )  #1
  step_num=givehint(prev_step,var_sym,False)
  # print("here",step_num)
  if step_num==1:
    #moving x term to lhs -->cxr=0
    cxl,cxr,cl,cr=giveCoeff(prev_step,var_sym)
    st2=""
    st2+=str(float(cxl-cxr))+"*"+var_sym
    st2+="="
    st2+=str(cr)
    prev_step=st2
    if(toprint):
      print("Next Step:  ",prev_step )  #2
  step_num=givehint(prev_step,var_sym,False)
  # print("here",step_num)
  if step_num==2:
    #Dividing the coeff of x to the rhs --> divide
    cxl,cxr,cl,cr=giveCoeff(prev_step,var_sym)
    st3=""
    st3+=var_sym
    st3+="="
    st3+=str(float(cr/cxl))
    prev_step=st3
    if(toprint):
      print("Next Step:  ",prev_step )  #3
    return float(cr/cxl)


def givenextstep(problem_equation,var_sym='x'): # Returns what should be the next Step While Solving a One-Variable Linear Equation
  curstep=givehint(problem_equation,var_sym)
  if curstep==0:
    cxl,cxr,cl,cr=giveCoeff(problem_equation,var_sym)
    st1=""
    st1+=str(cxl)+"*"+var_sym
    st1+="="
    st1+=str(cxr)+"*"+var_sym
    if cr-cl>0:
      st1+="+"
    st1+=str(cr-cl)
    ans_step=st1
  elif curstep==1:
    cxl,cxr,cl,cr=giveCoeff(problem_equation,var_sym)
    st2=""
    st2+=str(cxl-cxr)+"*"+var_sym
    st2+="="
    st2+=str(cr)
    ans_step=st2
  else:
    cxl,cxr,cl,cr=giveCoeff(problem_equation,var_sym)
    st3=""
    st3+=var_sym
    st3+="="
    st3+=str(float(cr/cxl))
    ans_step=st3
  print(ans_step)
  return(ans_step)


def solver_one_var(ques="3*x+5=8",var_sym='x'): # Main Function which Facilitates Solving of One Variable Linear Equation
  hintl1=0  #Simple Hint
  hintl2=0  #Asked Next Step
  hintl3=0  #Asked Complete Solution
  steps=0
  init_step=False
  prev=ques
  var_val=None
  ans=None
  while(init_step==False):
    
    print("Current Equation is:", prev)
    print("Now, we will try to simplify this Equation, inorder to reach towards the solution")
    print("Please choose among the following options:")
    print("0: Try solving the question")
    print("1: Please give hint")
    print("2: Help me with the next step")
    print("3: Give me the entire solution")
    print("4: I want to quit.")
    choice=int(input("Enter Your Choice : "))
    if choice==0:#solve-by-yourself
      curstep=input("Enter the Simplified Equation")
      res=evaluate(prev,curstep,var_sym)
      if res==1:
        prev=curstep
      if res==2:
        _,_,_,ans=giveCoeff(curstep,var_sym)
        init_step=True
      steps+=1
    elif choice==1:#hint
      givehint(prev,var_sym)
      hintl1+=1
    elif choice==2:#ask for next step
      tmp_prev=givenextstep(prev,var_sym)
      if(evaluate(prev,tmp_prev,var_sym)==2):
        _,_,_,ans=giveCoeff(tmp_prev,var_sym)
        init_step=True
      prev=tmp_prev
      hintl2+=1
    elif choice==3:#solve complete question by tutor
      ans=solver_step_wise(prev,var_sym,True)
      init_step=True
      hintl3+=1
    else:#quit
      print("Bhad Me Jao")
      return ans,hintl1,hintl2,hintl3,steps
  return ans,hintl1,hintl2,hintl3,steps










#####################################-- DOUBLE VARIABLE HELPER EQUATIONS --###################################

def calcExp(exp,var_sym='x'): #Helper Function for Evaluate
  if exp == "0":
    return (0,0)
  cx = len(re.findall(var_sym, exp))

  cc = 0
  k = exp.replace('-', '+').split('+')
  for i in k:
    if i!='' and var_sym not in i:
      cc += 1

  return (cc, cx)



def calcConsVars(eq,var_sym='x'): #Helper Function for Evaluate
  eq = ''.join(eq.split())
  [lhs, rhs] = eq.split('=')
  cc = cx = 0
  [tcc, tcx] = calcExp(lhs,var_sym)
  cc += tcc
  cx += tcx
  [tcc, tcx] = calcExp(rhs,var_sym)
  cc += tcc
  cx += tcx

  return (cc, cx)


def giveCoeffdouble(eq1,eq2="3*x+2*y=10"):
  x=sympy.Symbol('x')
  y=sympy.Symbol('y')
  l1, r1 = eq1.split('=')
  l2, r2 = eq2.split('=')
  exp_1=eval(l1)
  exp_2=eval(l2)
  # print(exp_left)
  # print(exp_right)
  # print(type(exp_left))
  # print(type(exp_right))

  
  x1=exp_1.coeff(x,1)
  y1=exp_1.coeff(y,1)
  
  x2=exp_2.coeff(x,1)
  y2=exp_2.coeff(y,1)
  
  # print(f"Coeff of x in 1 - {x1}")
  # print(f"Coeff of y in 1 - {y1}")
  # print(f"Constant in 1 - {r1}")
  # print(f"Coeff of x in 2 - {x2}")
  # print(f"Coeff of y in 2 - {y2}")
  # print(f"Constant in 2 - {r2}")
  return x1,y1,int(r1),x2,y2,int(r2)


# Python Program to find the L.C.M. of two input number

def compute_lcm(x, y):

   # choose the greater number
   if x > y:
       greater = x
   else:
       greater = y

   while(True):
       if((greater % x == 0) and (greater % y == 0)):
           lcm = greater
           break
       greater += 1

   return lcm



def solver_step_wise_double(eq1,eq2,begin=0,cf1=None,cf2=None): #Solves Double Variable Linear Equation in a Step-by-Step Manner and Returns the Solution of both Variables
  
  if cf1==None and cf2==None:
    t1,t2=find_coefficient(eq1,eq2)
  else:
    t1,t2=cf1,cf2

  x1,y1,r1,x2,y2,r2= giveCoeffdouble(eq1,eq2)

  x1=t1*x1
  y1=t1*y1
  r1=t1*r1
  st1=""
  st1=st1+str(x1)+'*x + '+ str(y1)+'*y = '+str(r1)
  
  x2=t2*x2
  y2=t2*y2
  r2=t2*r2
  st2=""
  st2=st2+str(x2)+'*x + '+ str(y2)+'*y = '+str(r2)
  
  if begin>=4:
    begin=0


  if begin==0:
    print("Full solution for the given equations are:")
    print("Equation 1: ",eq1)
    print("Equation 2: ",eq2)
    print('The coefficient to multiply with equation 1: ',t1)
    print('The coefficient to multiply with equation 2: ',t2)
    begin+=1

  if begin==1:
    print("Equation 1 after multiplying with coeffiecient: ",st1)
    print("Equation 2 after multiplying with coeffiecient: ",st2)
    begin+=1
  
  single_var_eq=str(y1-y2)+'*y = '+str(r1-r2)

  if begin==2:
    print("Subtracting equation 2 from equation 1, we get: ",single_var_eq)
    x_ans=solver_step_wise(single_var_eq,'y',True)
    begin+=1
  
  if begin==3:
    x_ans=solver_step_wise(single_var_eq,'y',False)
    #finding value of x using eq1
    x1,y1,r1,_,_,_= giveCoeffdouble(eq1)
    single_var_eq_2=str(x1)+'*x + '+ str(y1*x_ans)+'= '+str(r1)
    print("Substituting the Value of y in Equation 1: ",single_var_eq_2)
 
  
  y_ans=solver_step_wise(single_var_eq_2)
  return x_ans,y_ans


def solver_two_var(eq1="3*x+2*y=9",eq2="5*x-9*y=7"): #Main function which Facilitates solving of the Double Variable Linear 
  hintl1=0
  hintl2=0
  hintl3=0
  steps=0
  x_ans=None
  y_ans=None
  print("Equations are :", eq1," and ", eq2)

  ##########################################
  # Here we will get the number to multiply both the equations with to eliminate x variable
  init_step=False
  coef1=None
  coef2=None
  print("We want to eliminate x from the above two equations")
  while(init_step==False):
    print("Please choose among the following options:")
    print("0: Try solving the question")
    print("1: Please give hint")
    print("2: Help me with the next step")
    print("3: Give me the entire solution")
    print("4: I want to quit")
    choice=int(input("Enter Your Choice : "))
    if choice==0:#solve-by-yourself
      coef1=int(input("What number would you like to multiply with equn1"))
      coef2=int(input("What number would you like to multiply with equn2"))
      ch1,ch2=find_coefficient(eq1,eq2)
      if coef1==ch1 and coef2==ch2:
        print("Bazooka , Right values entered")
        init_step=True
      elif coef1/ch1==coef2/ch2:
        print("Values entered by you are correct , but they could have been simpler")
        init_step=True
      else:
        print("Values entered by you are wrong, Please Try Again")
      steps+=1
    elif choice==1:#hint
      print("Try to Find the LCM of coeff of x in eqn1 and eqn2")
      hintl1+=1
    elif choice==2:#ask for next step
      ch1,ch2=find_coefficient(eq1,eq2)
      print("First equn should be multiplied by ",ch1," and second equn should be multiplied by ", ch2)
      coef1=ch1
      coef2=ch2
      init_step=True
      hintl2+=1
    elif choice==3:#solve complete question by tutor
      x_ans,y_ans=solver_step_wise_double(eq1,eq2,0)
      hintl3+=1
      print('Solved Completely')
      return x_ans,y_ans,hintl1,hintl2,hintl3,steps
    else:#quit
      print("Bhad Me Jao")
      return x_ans,y_ans,hintl1,hintl2,hintl3,steps
  ###############################################
  #Here we will enter both the equations after multiplying them with the respective coefficients
  init_step=False
  print("Now, we need the two equations by multiplying the coefficients found earlier respectively")
  while(init_step==False):
    choice=int(input("Enter Your Choice : "))
    if choice==0:#solve-by-yourself
      coeff_eq1=input("Enter the first equation ")
      coeff_eq2=input("Enter the second equation ")
      #checking if it is correct
      coeff_x1,coeff_y1,coeff_r1,coeff_x2,coeff_y2,coeff_r2= giveCoeffdouble(coeff_eq1,coeff_eq2)
      x1,y1,r1,x2,y2,r2=giveCoeffdouble(eq1,eq2)
      if coeff_x1/x1==coeff_y1/y1 and coeff_y1/y1==coeff_r1/r1 and coeff_x2/x2==coeff_y2/y2 and coeff_y2/y2==coeff_r2/r2 and coeff_x1/x1==coef1 and coeff_x2/x2==coef2:
        print("Thats correct")
        init_step=True
      else:
        # print(coeff_x1/x1==coeff_y1/y1 , coeff_y1/y1==coeff_r1/r1 , coeff_x2/x2==coeff_y2/y2 , coeff_y2/y2==coeff_r2/r2 , coeff_x1/x1==coef1 , coeff_x2/x2==coef2)
        print("Equations input are incorrect, please try again!")
      steps+=1
    elif choice==1:#hint
      print("Multiply the whole equations by coeff of x in both eqn1 and eqn2")
      hintl1+=1
    elif choice==2:#ask for next step
      
      print("Now, the coeffients are multiplied with both the equations respectively:")
      x1,y1,r1,x2,y2,r2= giveCoeffdouble(eq1,eq2)
      x1=coef1*x1
      y1=coef1*y1
      r1=coef1*r1

      st1=""
      st1=st1+str(x1)+'*x + '+ str(y1)+'*y = '+str(r1)
      x2=coef2*x2
      y2=coef2*y2
      r2=coef2*r2
      st2=""
      st2=st2+str(x2)+'*x + '+ str(y2)+'*y = '+str(r2)
      print("Equation 1 after multiplying with coeffiecient: ",st1)
      print("Equation 2 after multiplying with coeffiecient: ",st2)

      hintl2+=1
      init_step=True
    elif choice==3:#solve complete question by tutor
      x_ans,y_ans=solver_step_wise_double(eq1,eq2,1,coef1,coef2)
      hintl3+=1
      print('Solved Completely')
      return x_ans,y_ans,hintl1,hintl2,hintl3,steps
    else:#quit
      print("Bhad Me Jao")
      return x_ans,y_ans,hintl1,hintl2,hintl3,steps


  ###########################################################
  #Here we will Substract the two equations after multiplying them with the respective coefficients

  init_step=False
  sub_eq=None
  print("Now, we need the result of substracting Equation 2 from Equation 1 that we got in previous step after multiplying the respective coefficients")
  while(init_step==False):
    choice=int(input("Enter Your Choice : "))
    if choice==0:#solve-by-yourself
      sub_eq=input("Enter the Resultant Equation after Substracting equation 2 from equation 1")
      subx,suby,subr,_,_,_=giveCoeffdouble(sub_eq)
      x1,y1,r1,x2,y2,r2=giveCoeffdouble(eq1,eq2)
      if subx==0 and suby==(coef1*y1-coef2*y2) and subr==(r1*coef1-r2*coef2):
        print("Thats correct")
        init_step=True
      else:
        print("Equation is incorrect, please try again!")
      steps+=1
    elif choice==1:#hint
      print("Please Substract the Equations Correctly on both sides i.e. LHS and RHS")
      hintl1+=1
    elif choice==2:#ask for next step
      
      # print("Now, the coeffients are multiplied with both the equations respectively:")
      x1,y1,r1,x2,y2,r2= giveCoeffdouble(eq1,eq2)
      x1=coef1*x1
      y1=coef1*y1
      r1=coef1*r1

      st1=""
      st1=st1+str(x1)+'*x + '+ str(y1)+'*y = '+str(r1)
      x2=coef2*x2
      y2=coef2*y2
      r2=coef2*r2
      st2=""
      st2=st2+str(x2)+'*x + '+ str(y2)+'*y = '+str(r2)

      single_var_eq=str(y1-y2)+'*y = '+str(r1-r2)
      print("Subtracting equation 2 from equation 1, we get: ",single_var_eq)
      sub_eq=single_var_eq
      init_step=True
      hintl2+=1
    elif choice==3:#solve complete question by tutor
      x_ans,y_ans=solver_step_wise_double(eq1,eq2,2,coef1,coef2)
      hintl3+=1
      print('Solved Completely')
      return x_ans,y_ans,hintl1,hintl2,hintl3,steps
    else:#quit
      print("Bhad Me Jao")
      return x_ans,y_ans,hintl1,hintl2,hintl3,steps

  #########################################################
  #We now have the Resultant Equation in only one variable y and we will solve for it here
  
  print('We now have the Resultant Equation in only one variable y and we will solve for it here')
  subx,suby,subr,_,_,_=giveCoeffdouble(sub_eq)
  sub_eq=str(suby)+"*"+"y"+"="+str(subr)

  y_ans,tmphl1,tmphl2,tmphl3,tstp=solver_one_var(sub_eq,'y')  #Subtracted Equation
  hintl1+=tmphl1
  hintl2+=tmphl2
  hintl3+=tmphl3
  steps+=tstp
  if (y_ans==None):
    return x_ans,y_ans,hintl1,hintl2,hintl3,steps
  print("We have Solved the Variable in one Variable y :",y_ans)
  #########################################################
  #We now will substitute the value of y here

  print("Now we will Substitute the Value of y in Equation 1 to form resulting equation")

  init_step=False
  subst_eq=None
  while(init_step==False):
    choice=int(input("Enter Your Choice : "))
    if choice==0:#solve-by-yourself
      tmp_subst_eq=input("Enter the Equation 1 after substituting the value of y :")
      substxl,_,subcl,subcr=giveCoeff(tmp_subst_eq)
      x1,y1,r1=giveCoeffdouble(eq1)

      if x1==substxl and subcl==y1*y_ans and r1==subcr:
        print("Thats correct")
        subst_eq=tmp_subst_eq
        init_step=True
      else:
        print("Equation is incorrect, please try again!")
      steps+=1
    elif choice==1:#hint
      print("Please Substitute the Values Correctly on both sides i.e. LHS and RHS")
      hintl1+=1
    elif choice==2:#ask for next step
      # print("Now, the coeffients are multiplied with both the equations respectively:")
      x1,y1,r1,_,_,_= giveCoeffdouble(eq1,eq2)

      st1=""
      st1+=str(x1)+'*x + '+ str(y1*y_ans)+' = '+str(r1)
      print("Substituting value of y in equation 1 we get: ",st1)
      subst_eq=st1
      init_step=True
      hintl2+=1
    elif choice==3:#solve complete question by tutor
      x_ans,y_ans=solver_step_wise_double(eq1,eq2,3,coef1,coef2)
      print('Solved Completely')
      hintl3+=1
      return x_ans,y_ans,hintl1,hintl2,hintl3,steps
    else:#quit
      print("Bhad Me Jao")
      return x_ans,y_ans,hintl1,hintl2,hintl3,steps
  ##########################################################################
  #We have the Resultant Equation in only one variable x and we will solve for it here

  x_ans,tmphl1,tmphl2,tmphl3,tstp=solver_one_var(subst_eq)
  hintl1+=tmphl1
  hintl2+=tmphl2
  hintl3+=tmphl3
  steps+=tstp

  if (x_ans==None):
    return x_ans,y_ans,hintl1,hintl2,hintl3,steps
  
  print("We have Solved the Variable in one Variable x :",x_val)

  ###########################################################################

  print("We have solved the Two Variable Equation")
  print('Solved Completely')
  return x_ans,y_ans,hintl1,hintl2,hintl3,steps



###############################-- Tutor Functions--##############################

def initialProblemGenerator(ques):
  
  #Now display the question
  print("Q) {0}".format(ques["questionString"]))

  hintl1 = 0
  steps = 0

  b_vars = False
  b_var_str = False
  b_eqs = False

  while not b_vars:
    s_num_vars = int(input("Enter the number of variables in the equation: "))
    if s_num_vars == ques["num_vars"]:
      b_vars = True
      print("You are correct!")
    else:
      print("This is the wrong answer. {0} is the correct answer.".format(ques["num_vars"]))
      hintl1 += 1
  
  while not b_var_str:
    x_str = input("What is the object corresponding x: ")

    if s_num_vars == 2:
      y_str = input("What is the object corresponding y: ")
    
    if x_str == ques["valueplaceHolderList"][0] and ((s_num_vars != 2) or (y_str == ques["valueplaceHolderList"][1])):
      b_var_str = True
      print("Great Keep Going.")
    else:
      print("This is wrong. Please Try Again.")
      print("x corresponds: {0}".format(ques["valueplaceHolderList"][0]))
      hintl1 += 1
      if s_num_vars == 2:
        print("y corresponds: {0}".format(ques["valueplaceHolderList"][1]))
  
  while not b_eqs:
    eq1 = input("Enter the first equation: ")
    if s_num_vars == 2:
      eq2 = input("Enter the second equation: ")

    if s_num_vars == 1:
      if giveCoeff(eq1) == giveCoeff(ques["equationList"][0]):
        print("Great! Now moving onto solving the equations.")
        b_eqs = True
    else:
      # solve for two variables and check. If true make b_eqs true
      if giveCoeffdouble(eq1, eq2) == giveCoeffdouble(ques["equationList"][0], ques["equationList"][1]) or giveCoeffdouble(eq2, eq1) == giveCoeffdouble(ques["equationList"][0], ques["equationList"][1]):
        print("Great! Now moving onto solving the equations.")
        b_eqs = True
    if not b_eqs:
      steps += 1
      print("The equations are incorrect. Please Try Again.")

  isSolved = False
  if s_num_vars == 1:
    (x_ans, t_hintl1, hintl2, hintl3, t_steps) = solver_one_var(eq1)
  else:
    (x_ans, y_ans, t_hintl1, hintl2, hintl3, t_steps) = solver_two_var(eq1, eq2)
  if x_ans != None:
    isSolved = True
  hintl1 += t_hintl1
  steps += t_steps

  

  return (hintl1, hintl2, hintl3, steps, isSolved)


student_profile={
    "name":None,
    "age":None,
    "academicClass":None,
    "currentLevel":None,
    "socialValueLevel": None, 
    "uniqueID":None, 
    "lastSessionTimeStamps":None,
    "timePerQuestion": None,
    "hintl1": None,
    "hintl2": None,
    "hintl3": None,
    "steps": None,
    "isSolved": None,
    "pastScores": None
}

try:
  f = open("ID_DATA.pickle", 'rb')
  ID_COUNT = pickle.load(f)
  f.close()
except:
  ID_COUNT = 0 

def createStudentProfile():
  global ID_COUNT
  global students
  print("Please input your name, age and academic class")
  student_profile["name"]= input("Name ")
  student_profile["age"]=input("Age ")
  student_profile["academicClass"]=input("Academic Qualification/Class ")
  student_profile["currentLevel"] = 1
  student_profile["socialValueLevel"] = 1
  student_profile["lastSessionTimeStamps"] = list()
  student_profile["timePerQuestion"] = list()
  student_profile["hintl1"] = list()
  student_profile["hintl2"] = list()
  student_profile["hintl3"] = list()
  student_profile["steps"] = list()
  student_profile["isSolved"] = list()
  student_profile["pastScores"] = list()

  ID_COUNT += 1

  student_profile["uniqueID"] = ID_COUNT

  students[ID_COUNT] = deepcopy(student_profile)
  return students[ID_COUNT]

def askSocialQ(st_q):
  print("Based on the above situation answer this social value based question.")
  print("Q) {0}".format(st_q["valueBasedQ"]))

  print("A) {0} B) {1} C){2} D){3}".format(st_q["optionsList"][0], st_q["optionsList"][1],st_q["optionsList"][2], st_q["optionsList"][3]) )

  st_val_str = input("Please enter the correct option(s): ")
  st_val_str = ''.join(st_val_str.split())
  st_val_str = ''.join(sorted(st_val_str.split(",")))
  
  ac_val_str = ''.join(st_q["correctOptionString"])

  if st_val_str == ac_val_str:
    print("\nYou have successfully solved the question\n")
    return True
  else:
    print("\nThis is incorrect. The correct options are: {0}\n".format(ac_val_str))
  
  return False


def computeScore(st_profile, time, hints, steps, social, ideal, isSolved):
  score = 0
  if len(st_profile["pastScores"]) != 0:
    score = st_profile["pastScores"][-1]
  
  if isSolved:
    score += 50
  score -= (steps - ideal) * 3
  if social:
    score += 20
  else:
    score -= 20

  #hints
  score -= (hints[0] * 5 + hints[1] * 10 + hints[2] * 20)
  

  return score


def tutor():

  global IDEAL_STEPS_SINGLE_VAR
  global IDEAL_STEPS_DOUBLE_VAR
  global students

  try:
    studentData = open("studentData.pickle", 'rb')
    students = pickle.load(studentData)
   # print(students)
    studentData.close()
  except:
   # print("COULDN'T OPEN")
   # students = dict()
   pass


  new_st = input("Are you an existing user? (Y/N) ")
  if new_st == "Y" or new_st == "y":
    st_id = input("Please enter you unique id: ")
    try:
      st_profile = students[int(st_id)]
    except:
      print("Enter a valid id")
      return
  else:
    #create the profile
    st_profile = createStudentProfile()
    st_id = st_profile["uniqueID"]
    print("{0} is your uniqueID.".format(st_id))


  #Now the student is logged in
  st_login_time = datetime.datetime.now()
  
  #user has been logged in, now ask the three options

  while True:

      print("What do you want to do right now?")
      op = int(input("0) Solve a question 1) Generate a report 2)Exit\n"))

      if op == 0:
        if st_profile["currentLevel"] == 1 and st_profile["socialValueLevel"] ==1:
          st_q = random.choice(questions["math_level_1"]["value_level_1"])
        elif st_profile["currentLevel"] == 1 and st_profile["socialValueLevel"] == 2:
          st_q = random.choice(questions["math_level_1"]["value_level_2"])
        elif st_profile["currentLevel"] == 2 and st_profile["socialValueLevel"] ==1:
          st_q = random.choice(questions["math_level_2"]["value_level_1"])
        else:
          st_q = random.choice(questions["math_level_2"]["value_level_2"])

        st_q_start_time = datetime.datetime.now()
        
        #call to yash's func
        (hintl1, hintl2, hintl3, steps, isSolved) = initialProblemGenerator(st_q)

        b_value_q = False
        #ask the social question
        if isSolved:
          b_value_q = askSocialQ(st_q)

        #stop the timeer
      
        st_q_end_time = datetime.datetime.now()

        #compute the score
        time = (st_q_end_time - st_q_start_time).total_seconds()



        st_score = computeScore(st_profile, time, [hintl1, hintl2, hintl3], steps, b_value_q, IDEAL_STEPS_SINGLE_VAR if st_q["num_vars"] == 1 else IDEAL_STEPS_DOUBLE_VAR, isSolved)

        st_profile["timePerQuestion"].append(time)
        st_profile["hintl1"].append(hintl1)
        st_profile["hintl2"].append(hintl2)
        st_profile["hintl3"].append(hintl3)
        st_profile["steps"].append(steps)
        st_profile["isSolved"].append(isSolved)
        st_profile["pastScores"].append(st_score)

        #update the level based on the score computed 
        #update the existing student existing student score and change the level
        if st_score <= 100:
          st_profile["currentLevel"] = 1
          st_profile["socialValueLevel"] = 1
        elif st_score <=200:
          st_profile["currentLevel"] = 1
          st_profile["socialValueLevel"] = 2
        elif st_score <= 300:
          st_profile["currentLevel"] = 2
          st_profile["socialValueLevel"] = 1
        else:
          st_profile["currentLevel"] = 2
          st_profile["socialValueLevel"] = 2
      
        print("\n\n")
        print("Current Question Stats: ")
        print("Time taken for Question: {0}\n seconds Hint Level1: {1}\n Hint Level2: {2}\n Hint Level3: {3}\n".format(time, hintl1, hintl2, hintl3))
        print("Steps: {0}\n Solved: {1}\n currentScore: {2}\n".format(steps, "Yes" if isSolved else "No", st_score))

      elif op == 1:
        #Genrate the user report

        print("\n\n")
        print("Name:{0}\n Age: {1}\n Class: {2}\n Unique ID: {3}\n".format(st_profile["name"], st_profile["age"], st_profile["academicClass"], st_profile["uniqueID"]))
        print("Current Level: {0} Current Social Value Level: {1}".format(st_profile["currentLevel"],st_profile["socialValueLevel"]))
        print("\n\n")

        #Generate the stats  
        if len(st_profile["steps"]) != 0:      
          print("Past Questions Stats:\n")
          print("Avg. Time per Question: {0}seconds\nAvg. Hint Level1: {1}\nAvg. int Level2: {2}\nAvg. Hint Level3: {3}\n".format(mean(st_profile["timePerQuestion"]), mean(st_profile["hintl1"]), mean(st_profile["hintl2"]), mean(st_profile["hintl3"])))
          print("Avg. Steps: {0}\nAvg. Number of Times Solved: {1}\nPast Score: {2}\n".format(mean(st_profile["steps"]), sum(st_profile["isSolved"]) / len(st_profile["steps"]), st_profile["pastScores"][-1]))
        else:
          print("Current Student Data not available. Solve more questions.")

      else:
        break;

  

  st_logout_time = datetime.datetime.now()

  st_profile["lastSessionTimeStamps"].append((st_login_time, st_logout_time))

  

  # store back the data in pickled file
  students[st_id] = st_profile
  #print(students)
  f = open("studentData.pickle", 'wb')
  pickle.dump(students, f)
  f.close()

  f = open("ID_DATA.pickle", 'wb')
  pickle.dump(ID_COUNT, f)
  f.close()



