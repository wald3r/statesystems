#---------------------------------------------------------------------
#      SCC (StateChart Compiler)
#           -- a compiler for an extended statechart formalism
#---------------------------------------------------------------------
#
# Copyright (C) 2003 Thomas Huining Feng
#
#---------------------------------------------------------------------
# Address:      MSDL, SOCS, McGill Univ., Montreal, Canada
# HomePage:     http://msdl.cs.mcgill.ca/people/tfeng/
# SCC HomePage: http://msdl.cs.mcgill.ca/people/tfeng/?research=scc
# Download:     http://savannah.nongnu.org/files/?group=svm
# CVS:          :pserver:anoncvs@subversions.gnu.org:/cvsroot/svm
#               (projects "svm" and "jsvm")
# Email:        hfeng2@cs.mcgill.ca
#---------------------------------------------------------------------
#
# This file is part of SCC.
#
#---------------------------------------------------------------------
# SCC is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# SCC is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SCC; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#---------------------------------------------------------------------


from string import *
from StringUtil import *
from EventHandler import EventHandler
from CodeGenerator import *
import time

class JavaGenerator(CodeGenerator):
  JavaHeader='\
// Java source code generated by SCC (StateChart Compiler) 0.3, written by Thomas Feng\n\
//   Source: [MODEL_FILE]\n\
//   Date:   [DATE]\n\
//   Time:   [TIME]\n\
[DESCRIPTION]\
\n\
// Header Section -- definition and module importation used by the following parts\n\
import java.io.*;\n\
\n\
class State {\n\
  public int StateID;\n\
  public State Next=null;\n\
  public State copy() {\n\
    State s=new State();\n\
    s.StateID=StateID;\n\
    if (Next!=null)\n\
      s.Next=Next.copy();\n\
    return s;\n\
  }\n\
}\n\
\n\
class History {\n\
  public int[] States;\n\
  public long[] Times;\n\
  public StateMachine Submodel;\n\
}\n\
\n\
class EventList {\n\
  public String Event;\n\
  public EventList Next=null;\n\
  public void Append(String e) {\n\
    EventList el=new EventList();\n\
    el.Event=e;\n\
    EventList cur=this;\n\
    while (cur.Next!=null && cur.Event!=e)\n\
      cur=cur.Next;\n\
    if (cur.Event!=e)\n\
      cur.Next=el;\n\
  }\n\
  public void Append(EventList el) {\n\
    while (el!=null) {\n\
      Append(el.Event);\n\
      el=el.Next;\n\
    }\n\
  }\n\
}\n\
\n\
class StringList {\n\
  public String str;\n\
  public StringList Next=null;\n\
  public StringList() {\n\
    this("");\n\
  }\n\
  public StringList(String str) {\n\
    this.str=str;\n\
  }\n\
  public StringList sort() {\n\
    StringList first, prev, next;\n\
    if (Next!=null) {\n\
      Next=Next.sort();\n\
      if (Next.str.compareTo(str)<0) {\n\
        first=Next;\n\
        prev=Next;\n\
        next=Next.Next;\n\
        while (next!=null && next.str.compareTo(str)<0) {\n\
          prev=next;\n\
          next=next.Next;\n\
        }\n\
        Next=next;\n\
        prev.Next=this;\n\
        return first;\n\
      }\n\
    }\n\
    return this;\n\
  }\n\
}\n\
\n\
class Hierarchy {\n\
  public String StateName;\n\
  public String PathName;\n\
  public int StateNum;\n\
  public int Level;\n\
  public Hierarchy Next;\n\
}\n\
\n\
class StateMachine {\n\
  protected int eventStr2Int(String event) {\n\
    return -1;\n\
  }\n\
  protected StringList getCurrentStateList() {\n\
    return null;\n\
  }\n\
  protected void topLevelHistory() {\n\
  }\n\
  public boolean Started=false;\n\
  public boolean Stopped=false;\n\
  public boolean handleEvent(String se) {\n\
    return false;\n\
  }\n\
  public String getCurrentState() {\n\
    return "[]";\n\
  }\n\
  public EventList getEnabledEvents() {\n\
    return null;\n\
  }\n\
  public void initModel() {\n\
  }\n\
  public boolean isInState(int s) {\n\
    return isInState(s, true);\n\
  }\n\
  public boolean isInState(int s, boolean use_backup) {\n\
    return false;\n\
  }\n\
  public boolean isInState(String s) {\n\
    return isInState(s, true);\n\
  }\n\
  public boolean isInState(String s, boolean use_backup) {\n\
    return false;\n\
  }\n\
  public int getParentState(int state) {\n\
    return -1;\n\
  }\n\
  public boolean isHistoryState(int state) {\n\
    return false;\n\
  }\n\
  public boolean isLeafState(String state) {\n\
    return true;\n\
  }\n\
  public Hierarchy getHierarchy() {\n\
    return getHierarchy(0, null);\n\
  }\n\
  public Hierarchy getHierarchy(int start_level, String state_prefix) {\n\
    return null;\n\
  }\n\
  protected void runActionCode(int code_num) {\n\
  }\n\
}\n\
\n'

  JavaTemplate='\
[HEADER]\
[ACCESSIBILITY]class [MODEL_NAME] extends StateMachine {\n\
  // Constants for this model\n\
  private static final int StateNum=[STATE_NUM];\n\
[EVENT_INT2STR_TABLE]\
[STATE_INT2STR_TABLE]\
[PARENT_TABLE]\
[HISTORY_STATE_TABLE]\
[LEAF_STATE_TABLE]\
[ORTHOGONAL_IN_BETWEEN]\
[ORTHOGONAL_TABLE]\
[HIERARCHY_DEFINITION]\
[COMMON_STATE_TABLE]\
  public static final String Description=[ESC_DESCRIPTION];\n\
\n\
  // Variables\n\
  private State state=null;\n\
  private State BackState=null;\n\
  private StateMachine[] Submodels=new StateMachine[StateNum];\n\
  private History[] history=new History[StateNum];\n\
  private long HistoryCount=0;\n\
\n\
  // Constructor\n\
  public [MODEL_NAME]() {\n\
    for (int i=0; i<StateNum; i++) {\n\
      history[i]=new History();\n\
      history[i].States=new int[StateNum];\n\
      history[i].Times=new long[StateNum];\n\
      for (int j=0; j<StateNum; j++) {\n\
        history[i].States[j]=-1;\n\
        history[i].Times[j]=-1;\n\
      }\n\
    }\n\
  }\n\
\n\
  // Methods\n\
  private boolean isParent(int sp, int sc) {\n\
    return sc>=0 && (sp<0 || Hierarchy[sp][sc]);\n\
  }\n\
  public boolean isInState(int s, boolean use_backup) {\n\
    State st;\n\
    if (use_backup)\n\
      st=BackState;\n\
    else\n\
      st=state;\n\
    while (st!=null) {\n\
      if (st.StateID==s || isParent(s, st.StateID))\n\
        return true;\n\
      else\n\
        st=st.Next;\n\
    }\n\
    return false;\n\
  }\n\
  public boolean isInState(String s, boolean use_backup) {\n\
    for (int i=0; i<StateNum; i++)\n\
      if (s.compareTo(StateNames[i])==0)\n\
        return isInState(i, use_backup);\n\
    for (int i=0; i<StateNum; i++)\n\
      if (Submodels[i]!=null && s.startsWith(StateNames[i]+".")) {\n\
        String SubmodelState=s.substring(StateNames[i].length()+1);\n\
        return isInState(i, use_backup) && Submodels[i].isInState(SubmodelState, use_backup);\n\
      }\n\
    return false;\n\
  }\n\
  public static void main(String[] argv) {\n\
[INTERFACE]\
  }\n\
  public void initModel() {\n\
[INIT_CODE]\
  }\n\
  public boolean handleEvent(String se) {\n\
[EVENT_CODE]\
  }\n\
  public void applyMask(boolean[] mask, boolean[] dest) {\n\
    for (int i=0; i<StateNum; i++)\n\
      dest[i]=dest[i] && mask[i];\n\
  }\n\
  public void forceIntoState(int s) {\n\
    boolean changed=false;\n\
    State s2=state;\n\
    while (s2!=null) {\n\
      boolean HasCommonParent=false;\n\
      for (int i=0; i<StateNum; i++) {\n\
        if (isParent(i, s2.StateID) && isParent(i, s)) {\n\
          HasCommonParent=true;\n\
          if (!hasOrthogonalStateInBetween(i, s2.StateID)) {\n\
            changeState(s2.StateID, s);\n\
            changed=true;\n\
          }\n\
        }\n\
      }\n\
      if (!HasCommonParent) {\n\
        changeState(s2.StateID, s);\n\
        changed=true;\n\
      }\n\
      s2=s2.Next;\n\
    }\n\
    if (!changed)\n\
      addInState(s);\n\
  }\n\
  public void changeState(int s1, int s2) {\n\
    changeState(s1, s2, false);\n\
  }\n\
  public void changeState(int s1, int s2, boolean check_history) {\n\
    // t1=common(s1, s2)\n\
    int t1=CommonStateTable[s1][s2];\n\
    recordHistory(t1);\n\
    if (t1>=0)\n\
      removeOutStates(t1);\n\
    else\n\
      state=null;\n\
    // t2=history(s2)\n\
    int t2=HistoryStateTable[s2];\n\
    if (t2==0) // no history\n\
      generateStates(t1, s2);\n\
    else if (t2==1) // normal history\n\
      if (!check_history)\n\
        generateStates(t1, s2);\n\
      else if (hasHistoryRecorded(s2))\n\
        generateStates(t1, history[s2].States[s2]);\n\
      else\n\
        generateStates(t1, s2, 1);\n\
    else if (t2==2) // deep history\n\
      if (check_history && hasHistoryRecorded(s2))\n\
        for (int i=0; i<StateNum; i++) {\n\
          int hs=history[s2].States[i];\n\
          if (hs>=0 && isLeafState(hs))\n\
            addInState(hs);\n\
        }\n\
      else\n\
        generateStates(t1, s2);\n\
  }\n\
  private boolean addInState(int s) {\n\
    if (!isInState(s, false)) {\n\
      State st=new State();\n\
      st.StateID=s;\n\
      st.Next=state;\n\
      state=st;\n\
      return true;\n\
    }\n\
    else\n\
      return false;\n\
  }\n\
  private void generateStates(int common, int dest) {\n\
    generateStates(common, dest, 0);\n\
  }\n\
  private void generateStates(int common, int dest, int history_type) {\n\
[STATES_CODE]\
  }\n\
  private void removeOutStates(int common_state) {\n\
    State s=state, prev=null;\n\
    while (s!=null) {\n\
      if (isParent(common_state, s.StateID)) {\n\
        if (prev==null)\n\
          state=state.Next;\n\
        else\n\
          prev.Next=s.Next;\n\
      }\n\
      else\n\
        prev=s;\n\
      s=s.Next;\n\
    }\n\
  }\n\
  protected int eventStr2Int(String event) {\n\
    for (int i=0; i<[EVENT_NUM]; i++)\n\
      if (event.compareTo(EventNames[i])==0)\n\
        return i;\n\
    return -1;\n\
  }\n\
  private String stateInt2Str(int state) {\n\
    if (state==-1)\n\
      return "";\n\
    else\n\
      return StateNames[state];\n\
  }\n\
  protected StringList getCurrentStateList() {\n\
    StringList sl=new StringList(), slend=sl;\n\
    State s=state;\n\
    while (s!=null) {\n\
      StateMachine sm=Submodels[s.StateID];\n\
      String curstate=stateInt2Str(s.StateID);\n\
      if (sm!=null) {\n\
        slend.Next=sm.getCurrentStateList();\n\
        while (slend.Next!=null) {\n\
          slend.Next.str=curstate+"."+slend.Next.str;\n\
          slend=slend.Next;\n\
        }\n\
      }\n\
      else {\n\
        slend.Next=new StringList(curstate);\n\
        slend=slend.Next;\n\
      }\n\
      s=s.Next;\n\
    }\n\
    return sl.Next;\n\
  }\n\
  public String getCurrentState() {\n\
    return getCurrentState(null);\n\
  }\n\
  private String getCurrentState(StringList states) {\n\
    String strst;\n\
    if (states==null) {\n\
      states=getCurrentStateList();\n\
      if (states!=null) {\n\
        states=states.sort();\n\
        strst="[\\\'"+states.str+"\\\'"+getCurrentState(states)+"]";\n\
      }\n\
      else\n\
        strst="[]";\n\
    }\n\
    else {\n\
      if (states.Next!=null)\n\
        strst=", \\\'"+states.Next.str+"\\\'"+getCurrentState(states.Next);\n\
      else\n\
        strst="";\n\
    }\n\
    return strst;\n\
  }\n\
  public int getParentState(int state) {\n\
    return ParentTable[state];\n\
  }\n\
  public boolean isHistoryState(int state) {\n\
    return HistoryStateTable[state]>0;\n\
  }\n\
  private boolean isLeafState(int state) {\n\
    return LeafStateTable[state]!=null;\n\
  }\n\
  public boolean isLeafState(String state) {\n\
    for (int i=0; i<StateNum; i++) {\n\
      if (LeafStateTable[i]==null)\n\
        continue;\n\
      if (state.compareTo(LeafStateTable[i])==0 && Submodels[i]==null)\n\
        return true;\n\
      else if (state.startsWith(LeafStateTable[i]+".") && Submodels[i]!=null) {\n\
        String SubmodelState=state.substring(LeafStateTable[i].length()+1);\n\
	return Submodels[i].isLeafState(SubmodelState);\n\
      }\n\
    }\n\
    return false;\n\
  }\n\
  private boolean isHistoryUp2Date(int state, long time) {\n\
    for (int i=0; i<StateNum; i++)\n\
      if (history[state].Times[i]>=time)\n\
        return true;\n\
    return false;\n\
  }\n\
  private void mergeHistory(int state, int[] states, long[] times) {\n\
    long max=-1;\n\
    for (int i=0; i<StateNum; i++)\n\
      if (times[i]>max)\n\
        max=times[i];\n\
    if (isHistoryUp2Date(state, max)) {\n\
      for (int i=0; i<StateNum; i++)\n\
        if (times[i]>history[state].Times[i]) {\n\
          history[state].States[i]=states[i];\n\
          history[state].Times[i]=times[i];\n\
        }\n\
    }\n\
    else {\n\
      history[state].States=(int[])states.clone();\n\
      history[state].Times=(long[])times.clone();\n\
    }\n\
  }\n\
  private void recordHistory(int top_state) {\n\
    long time=HistoryCount++;\n\
    State s=state;\n\
    while (s!=null) {\n\
      int child=s.StateID;\n\
      int[] states=new int[StateNum];\n\
      long[] times=new long[StateNum];\n\
      for (int i=0; i<StateNum; i++) {\n\
        states[i]=-1;\n\
        times[i]=-1;\n\
      }\n\
      states[child]=child;\n\
      times[child]=time;\n\
      if (top_state<0 || isParent(top_state, child)) {\n\
        int parent=getParentState(child);\n\
        if (isHistoryState(child))\n\
          history[child].Submodel=Submodels[child];\n\
        while (parent>=0 && times[parent]!=time) {\n\
          states[parent]=child;\n\
          times[parent]=time;\n\
          if (isHistoryState(parent))\n\
            mergeHistory(parent, states, times);\n\
          if (parent==top_state)\n\
            break;\n\
          child=parent;\n\
          parent=getParentState(child);\n\
        }\n\
      }\n\
      s=s.Next;\n\
    }\n\
  }\n\
  private boolean hasHistoryRecorded(int state) {\n\
    for (int i=0; i<StateNum; i++) {\n\
      if (history[state].States[i]!=-1)\n\
        return true;\n\
      if (Submodels[state]!=null)\n\
        return true;\n\
    }\n\
    return false;\n\
  }\n\
  private boolean hasOrthogonalStateInBetween(int parent, int leaf) {\n\
    return OrthogonalInBetween[parent+1][leaf];\n\
  }\n\
  private boolean check_history(int dest) {\n\
    State s=state;\n\
    while (s!=null) {\n\
      if (isParent(dest, s.StateID) && !hasOrthogonalStateInBetween(dest, s.StateID))\n\
        return false;\n\
      s=s.Next;\n\
    }\n\
    return true;\n\
  }\n\
  public EventList getEnabledEvents() {\n\
[ENABLED_EVENTS_CODE]\
  }\n\
  public Hierarchy getHierarchy(int start_level, String state_prefix) {\n\
[HIERARCHY_CODE]\
  }\n\
  protected void topLevelHistory() {\n\
    int s=state.StateID, t;\n\
    do {\n\
      t=getParentState(s);\n\
      if (t!=-1)\n\
        s=t;\n\
    } while (t!=-1);\n\
    changeState(s, s);\n\
  }\n\
  protected void runActionCode(int code_num) {\n\
[ACTION_CODE]\
  }\n\
}\n\
\n\
[OTHER_MODELS]'
    
  TextInterface='\
    [MODEL_NAME] model=new [MODEL_NAME]();\n\
    if ([MODEL_NAME].Description!=null)\n\
      System.out.println([MODEL_NAME].Description);\n\
    String cmd="";\n\
    model.initModel();\n\
    InputStreamReader isr=new InputStreamReader(System.in);\n\
    BufferedReader br=new BufferedReader(isr);\n\
    while (cmd!=null && cmd.compareTo("exit")!=0) {\n\
      try {\n\
        System.out.print(model.getCurrentState()+" > ");\n\
        cmd=br.readLine();\n\
        if (cmd==null || cmd.compareTo("exit")==0)\n\
          break;\n\
        if (!model.Stopped)\n\
          model.handleEvent(cmd);\n\
      }\n\
      catch (IOException e1) {\n\
        System.out.println("Input error!");\n\
      }\n\
    }\n'

  def __init__(self, eventhandler):
    CodeGenerator.__init__(self, eventhandler, "java")

  def generate_code(self, need_header=1, public_class=1):

    self.init_generator()
    
    header=JavaGenerator.JavaTemplate

    localtime=time.localtime()
    months=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    if self.eventhandler.description:
      desc="//\nModel Description:\n"+self.eventhandler.description
      x=0
      while x<len(desc):
        if desc[x]=='\n':
	  desc=desc[:x]+"\n//   "+desc[x+1:]
        x=x+1
      desc=desc+"\n"
    else:
      desc=""
    self.model_name=self.eventhandler.options[MODEL_NAME]
    if self.eventhandler.description:
      description=escape(self.eventhandler.description)
    else:
      description="null"
    macros={"[MODEL_FILE]": self.eventhandler.model_name,
	    "[DATE]": "%s %d, %d" % (months[localtime[1]-1], localtime[2], localtime[0]),
	    "[TIME]": "%d:%d:%d" % (localtime[3], localtime[4], localtime[5]),
	    "[DESCRIPTION]": desc,
            "[ESC_DESCRIPTION]": description,
            "[INTERFACE]": JavaGenerator.TextInterface,
            "[MODEL_NAME]": self.model_name,
            "[INIT_CODE]": self.find_initial_state(self.eventhandler.stateH),
	    "[HIERARCHY_DEFINITION]": self.generate_hierarchy_def(),
	    "[OTHER_MODELS]": self.generate_other_models(),
	    "[STATES_CODE]": self.generate_states_code(),
	    "[EVENT_INT2STR_TABLE]": self.generate_event_int2str_table(),
	    "[STATE_INT2STR_TABLE]": self.generate_state_int2str_table(),
	    "[STATE_NUM]": str(self.state_num),
	    "[EVENT_NUM]": str(self.event_num),
	    "[EVENT_CODE]": self.generate_event_code(),
	    "[PARENT_TABLE]": self.generate_parent_table(),
	    "[HISTORY_STATE_TABLE]": self.generate_history_state_table(),
	    "[LEAF_STATE_TABLE]": self.generate_leaf_state_table(),
	    "[ORTHOGONAL_IN_BETWEEN]": self.generate_orthogonal_in_between_table(),
            "[ORTHOGONAL_TABLE]": self.generate_orthogonal_table(),
            "[COMMON_STATE_TABLE]": self.generate_common_state_table(),
	    "[ENABLED_EVENTS_CODE]": self.generate_enabled_events_code(),
	    "[HIERARCHY_CODE]": self.generate_hierarchy_code(),
	    "[ACTION_CODE]": self.generate_action_code()}
    
    if need_header:
      macros["[HEADER]"]=JavaGenerator.JavaHeader
    else:
      macros["[HEADER]"]=''
    if public_class:
      macros["[ACCESSIBILITY]"]='// Main Class -- the top level model that is executed from the command line\n\
public '
    else:
      macros["[ACCESSIBILITY]"]=''

    priority_macros=["[INTERFACE]", "[HEADER]"]
    return replace_macros(header, priority_macros, macros)

  def generate_hierarchy_def(self):
    codes=[]
    comments=[]
    ps=0
    states=self.state_table2.keys()
    states.sort()
    while ps<len(states):
      code="{"
      cs=0
      while cs<len(states):
        if cs>0:
          code=code+", "
        if cs!=ps and self.eventhandler.is_or_is_substate(states[cs], states[ps]):
          code=code+"true "
        else:
          code=code+"false"
        cs=cs+1
      code=code+"}"
      codes.append(code)
      comments.append("children for state %s" % states[ps])
      ps=ps+1
    return self.generate_array("static final boolean[][]", "Hierarchy", codes, comments)

  def generate_event_code(self):
    code='\
    boolean handled=false;\n\
    int e=eventStr2Int(se);\n\
    boolean[] table=new boolean[%d];\n\
    for (int i=0; i<%d; i++)\n\
      table[i]=true;\n\
    BackState=state.copy();\n\
    switch (e) {\n' % (self.state_num, self.state_num)
    keys=self.eventhandler.trans.keys()
    keys.sort()
    for t in keys:
      code=code+'\
      case %d: // event "%s"\n' % (self.event_table2[t], t) + self.generate_check_state_code(self.eventhandler.trans, t)
    code=code+'\
    }\n'
    keys=self.submodels.keys()
    keys.sort()
    for k in keys:
      code=code+'\
    if (table[%d] && isInState(%d) && Submodels[%d].handleEvent(se)) {\n\
      applyMask(OrthogonalTable[%d], table);\n\
      handled=true;\n\
    }\n' % (k, k, k, k)
    code=code+'\
    return handled;\n'
    return code

  def generate_check_state_code(self, trans, e):
    code=''
    for t in trans[e]:
      stnum=self.get_state_num(t['S'])
      code=code+'\
        if (table[%d] && isInState(%d)) {\n' % (stnum, stnum)
      if self.eventhandler.is_ifs(t['S']):
        keys=self.submodels.keys()
        keys.sort()
        for k in keys:
          path=self.state_table1[int(k)]
          if self.eventhandler.is_or_is_substate(path, t['S']):
            if path!=t['S']:
              code=code+'\
          if (table[%d] && isInState(%d) && Submodels[%d].handleEvent(se)) {\n\
            applyMask(OrthogonalTable[%d], table);\n\
            handled=true;\n\
          }\n' % (k, k, k, k)
	    else:
	      code=code+'\
          if (table[%d] && Submodels[%d].handleEvent(se)) {\n\
            applyMask(OrthogonalTable[%d], table);\n\
            handled=true;\n\
          }\n' % (k, k, k)
      [p, sp]=self.find_submodel_path(t['N'])
      if t[HISTORY_STATE]:
	chkhs=", true"
      else:
	chkhs=""
      if sp:  # transition into a submodel
	pnum=self.get_state_num(p)
	code=code+'\
          changeState(%s, %s%s);\n\
          Submodels[%d].forceIntoState(%d);\n' % (self.get_state_num(t['S']), pnum, pnum, self.generated_models[self.submodels[pnum]].get_state_num(sp), chkhs)
      else:
        code=code+'\
          changeState(%s, %s%s);\n' % (self.get_state_num(t['S']), self.get_state_num(t['N']), chkhs)

      code=code+'\
          applyMask(OrthogonalTable[%d], table);\n\
          handled=true;\n\
        }\n' % self.get_state_num(t['S'])
      
    code=code+'\
        break;\n'
    return code

  def generate_states_code(self, stateH=None, path="", code=""):
    first=0
    sk=self.state_table2.keys()
    sk.sort()
    if not code:
      first=1
      stateH=self.eventhandler.stateH
      code=code+"\
    switch (common) {\n\
      case -1:\n\
        switch (dest) {\n"
      for s in sk:
	code=code+"\
          case %d:\n" % self.get_state_num(s) \
	    + "\
            if (history_type!=2 || check_history(-1)) {\n" \
	    + self.generate_in_states(stateH, "", s) \
	    + "\
            }\n\
            break;\n"
      code=code+"\
        }\n\
        break;\n"
    keys=stateH.keys()
    keys.sort()
    for k in keys:
      if not k in StateProperties:
	newpath=self.eventhandler.append_path(path, k)
	code=code+"\
      case %d:\n\
        switch (dest) {\n" % self.get_state_num(newpath)
	for s in sk:
	  if self.eventhandler.is_or_is_substate(s, newpath):
	    code=code+"\
          case %d:\n" % self.get_state_num(s) \
	    + "\
            if (history_type!=2 || check_history(%d)) {\n" % self.get_state_num(newpath) \
	    + self.generate_in_states(stateH[k], newpath, s) \
	    + "\
            }\n\
            break;\n"
        code=code+"\
        }\n\
        break;\n"
	code=self.generate_states_code(stateH[k], newpath, code)
    if first:
      code=code+"\
    }\n"
    return code

  def generate_in_states(self, stateH, com, des):
    desnum=self.get_state_num(des)
    code=''
    dpaths=split(des, '.')
    if com:
      cpaths=split(com, '.')
    else:
      cpaths=[]
    states=stateH
    i=len(cpaths)
    loopin=0
    if i<len(dpaths):
      p=dpaths[i]
      if states[p][CONCURRENT_STATE]:
	keys=states.keys()
	keys.sort()
	for s in keys:
	  if not s in StateProperties:
	    loopin=1
	    next_com=self.eventhandler.append_path(com, s)
            code=code+'\
            if (history_type!=2 || check_history(%d)) {\n' % self.get_state_num(next_com)
            if self.is_final_state(next_com):
              code=code+'\
            Stopped=true;\n'
	    if s!=p:
	      code=code+self.generate_in_states(states[s], next_com, next_com)
	    else:
	      code=code+self.generate_in_states(states[s], next_com, des)
	    code=code+'\
            }\n'
      else:
	loopin=1
	next_com=self.eventhandler.append_path(com, p)
        code=code+'\
            if (history_type!=2 || check_history(%d)) {\n' % self.get_state_num(next_com)
        if self.is_final_state(next_com):
          code=code+'\
            Stopped=true;\n'
	code=code+self.generate_in_states(states[p], next_com, des)
	code=code+'\
            }\n'
      i=i+1
    if not loopin:
      found_def=0
      keys=states.keys()
      keys.sort()
      for s in keys:
	if not s in StateProperties and (states[s][DEFAULT_STATE] or states[s][CONCURRENT_STATE]):
	  found_def=1
	  next_com=self.eventhandler.append_path(com, s)
          code=code+'\
            if (history_type!=2 || check_history(%d)) {\n' % self.get_state_num(next_com)
          if self.is_final_state(next_com):
            code=code+'\
            Stopped=true;\n'
	  code=code+self.generate_in_states(states[s], next_com, next_com)
	  code=code+'\
            }\n'
      if not found_def:
	code=code+'\
            addInState(%d);  // move into leaf state "%s"\n' % (desnum, des)
        if self.is_final_state(des):
          code=code+'\
            Stopped=true;\n'
	stnum=self.get_state_num(des)
	if self.submodels.has_key(stnum):
	  code=code+'\
            if (history_type==1 && Submodels[%d]!=null)\n\
              Submodels[%d].topLevelHistory();\n\
            else if (history_type!=2 || Submodels[%d]==null) {\n\
              boolean print_desc=Submodels[%d]==null;\n\
              Submodels[%d]=new %s();\n\
              if (print_desc && %s.Description!=null)\n\
                System.out.println(%s.Description);\n\
              Submodels[%d].initModel();\n\
            }\n' % (stnum, stnum, stnum, stnum, stnum, self.submodels[stnum], self.submodels[stnum], self.submodels[stnum], stnum)
    return code

  def generate_array(self, atype, aname, alist, comments=None):
    code="\
  private %s %s={" % (atype, aname)
    space=(13+len(atype)+len(aname))
    i=0
    while i<len(alist):
      k=alist[i]
      code=code+str(k)
      if i<len(alist)-1:
	code=code+","
      else:
        code=code+" "
      if comments:
	code=code+"  // "+comments[i]
      if i<len(alist)-1:
        code=code+"\n"+" "*space
      else:
	code=code+"\n"+" "*(space-1)
      i=i+1
    code=code+"};\n"
    return code

  def generate_event_int2str_table(self):
    events=[]
    keys=self.event_table1.keys()
    keys.sort()
    for k in keys:
      events.append('"%s"' % self.event_table1[k])
    return self.generate_array("static final String[]", "EventNames", events)

  def generate_state_int2str_table(self):
    states=[]
    keys=self.state_table1.keys()
    keys.sort()
    for k in keys:
      states.append('"%s"' % self.state_table1[k])
    return self.generate_array("static final String[]", "StateNames", states)

  def find_initial_state(self, stateH, path=''):
    """ To find the initial state(s) in the state hierachy, stateH.
    """
    code=''
    keys=stateH.keys()
    keys.sort()
    for s in keys:
      if not s in StateProperties:
        if stateH[s][DEFAULT_STATE]:
          newstateH=stateH[s]
	  newpath=self.eventhandler.append_path(path, s)
	  stnum=self.get_state_num(newpath)
          code=code+self.find_initial_state(newstateH, newpath)
	  has_substate=0
	  skeys=stateH[s].keys()
	  skeys.sort()
	  for ss in skeys:
	    if not ss in StateProperties:
	      has_substate=1
	      break
	  if not has_substate:
	    code=code+'\
    addInState(%s); // init state "%s"\n' % (self.get_state_num(newpath), newpath)
            if self.is_final_state(newpath):
              code=code+'\
    Stopped=true;\n'
	    if self.submodels.has_key(stnum):
	      code=code+'\
    Submodels[%d]=new %s();\n\
    if (%s.Description!=null)\n\
      System.out.println(%s.Description);\n\
    Submodels[%d].initModel();\n' % (stnum, self.submodels[stnum], self.submodels[stnum], self.submodels[stnum], stnum)
    if path=="":
      code=code+'\
    Started=true;\n'

    return code

  def generate_other_models(self):
    code=''
    for eh in self.required_models:
      if not self.compiled_models.has_key(eh.options[MODEL_NAME]):
	self.compiled_models[eh.options[MODEL_NAME]]=eh
	jg=JavaGenerator(eh)
	code=code+'\
// Submodel Class "%s" -- the submodel executed by the top-level model\n' % eh.options[MODEL_NAME] + jg.generate_code(0, 0)
	self.generated_models[eh.options[MODEL_NAME]]=jg
    return code

  def generate_parent_table_rec(self, stateH, plist, comments, pnum=-1, path=""):
    keys=stateH.keys()
    keys.sort()
    for k in keys:
      if not k in StateProperties:
	newpath=self.eventhandler.append_path(path, k)
	cnum=self.get_state_num(newpath)
	plist[cnum]=pnum
	comments[cnum]="%s -- parent " % newpath
	if path:
	  comments[cnum]=comments[cnum]+path
	else:
	  comments[cnum]=comments[cnum]+"(None)"
	self.generate_parent_table_rec(stateH[k], plist, comments, cnum, newpath)
    
  def generate_parent_table(self):
    plist=[]
    comments=[]
    i=0
    while i<self.state_num:
      plist.append(-1);
      comments.append("");
      i=i+1
    self.generate_parent_table_rec(self.eventhandler.stateH, plist, comments)
    return self.generate_array("static final int[]", "ParentTable", plist, comments)

  def generate_history_state_table(self):
    htable=[]
    keys=self.state_table2.keys()
    keys.sort()
    for s in keys:
      htable.append(str(self.has_history_state(s)))
    return self.generate_array("static final int[]", "HistoryStateTable", htable)

  def generate_leaf_state_table(self):
    ltable=[]
    keys=self.state_table2.keys()
    keys.sort()
    for s in keys:
      if self.is_leaf_state(s, 0):
	ltable.append('"%s"' % s);
      else:
	ltable.append('null');
    return self.generate_array("static final String[]", "LeafStateTable", ltable)

  def generate_orthogonal_in_between_table(self):
    table=[]
    i=0
    while i<self.state_num+1:
      table.append([])
      j=0
      while j<self.state_num:
	table[i].append(0)
        j=j+1
      i=i+1
    hs=[]
    keys=self.state_table2.keys()
    keys.sort()
    for k in keys:
      if self.has_orthogonal_substate(k):
        hs.append(k)
    if len(hs)>0:
      keys=self.state_table1.keys()
      keys.sort()
      for s1 in keys+[-1]:
        foundhist=0
        hist=[]
        for h in hs:
          if s1==-1 or self.eventhandler.is_or_is_substate(h, self.state_table1[s1]):
            foundhist=1
            hist.append(h)
        if foundhist:
          skeys=self.state_table2.keys()
	  skeys.sort()
          for s2 in skeys:
	    if not self.is_leaf_state(s2):
	      continue
            foundhist=0
            for h in hist:
              if self.eventhandler.is_or_is_substate(s2, h):
	        foundhist=1
	        break
	    if foundhist:
	      table[s1+1][self.get_state_num(s2)]=1
    codes=[]
    for hs in table:
      i=0
      code="{"
      while i<self.state_num:
	if hs[i]:
	  code=code+"true "
	else:
	  code=code+"false"
	if i<self.state_num-1:
	  code=code+", "
	i=i+1
      code=code+"}"
      codes.append(code)
    return self.generate_array("static final boolean[][]", "OrthogonalInBetween", codes)

  def generate_orthogonal_table_rec(self, stateH, path, table, orthogonal):
    if path:
      snum=self.get_state_num(path)
      for o in orthogonal:
        if not self.eventhandler.is_or_is_substate(path, o):
          onum=self.get_state_num(o)
          table[snum][onum]=1
          table[onum][snum]=1
    neworthogonal=[]
    for s in stateH.keys():
      if not s in StateProperties:
        if stateH[s][CONCURRENT_STATE]:
          neworthogonal.append(self.eventhandler.append_path(path, s))
    for s in stateH.keys():
      if not s in StateProperties:
        self.generate_orthogonal_table_rec(stateH[s], self.eventhandler.append_path(path, s), table, orthogonal+neworthogonal)
    
  def generate_orthogonal_table(self):
    i=0
    table=[]
    while i<self.state_num:
      table.append([])
      j=0
      while j<self.state_num:
        table[i].append(0)
        j=j+1
      i=i+1
    self.generate_orthogonal_table_rec(self.eventhandler.stateH, "", table, [])
    i=0
    while i<self.state_num:
      j=0
      s='{'
      while j<self.state_num:
        if table[i][j]:
          s=s+'true'
        else:
          s=s+'false'
        if j<self.state_num-1:
          s=s+', '
        j=j+1
      s=s+'}'
      table[i]=s
      i=i+1
    return self.generate_array("static final boolean[][]", "OrthogonalTable", table)
  
  def generate_common_state_table(self):
    codes=[]
    i=0
    while i<self.state_num:
      j=0
      code="{"
      while j<self.state_num:
        com=self.eventhandler.common_state(self.state_table1[i], self.state_table1[j])
        if com:
          comnum=self.get_state_num(com)
        else:
          comnum=-1
        code=code+str(comnum)
        if j<self.state_num-1:
          code=code+", "
        else:
          code=code+"}"
        j=j+1
      codes.append(code)
      i=i+1
    return self.generate_array("static final int[][]", "CommonStateTable", codes)

  def generate_enabled_events_code(self):
    code="\
    EventList events=new EventList();\n"
    keys=self.eventhandler.trans.keys()
    keys.sort()
    for k in keys:
      for t in self.eventhandler.trans[k]:
        code=code+"\
    if (isInState(%d))\n\
      events.Append(\"%s\");\n" % (self.state_table2[t['S']], k)
    keys=self.submodels.keys()
    keys.sort()
    for k in keys:
      code=code+"\
    if (isInState(%d))\n\
      events.Append(Submodels[%d].getEnabledEvents());\n" % (k, k)
    code=code+"\
    return events.Next;\n"
    return code

  def generate_hierarchy_code_rec(self, code, stateH, level=0, path=""):
    keys=stateH.keys()
    keys.sort()
    for k in keys:
      if not k in StateProperties:
	newpath=self.eventhandler.append_path(path, k)
	snum=self.get_state_num(newpath)
	code=code+'\
    // Generate state "%s" in the hierarchy table\n\
    lasth.Next=new Hierarchy();\n\
    lasth.Next.StateName="%s";\n\
    lasth.Next.PathName=state_prefix==null?"%s":state_prefix+".%s";\n\
    lasth.Next.StateNum=%d;\n\
    lasth.Next.Level=start_level+%d;\n\
    lasth=lasth.Next;\n' % (newpath, k, newpath, newpath, snum, level)
	if self.submodels.has_key(snum):
	  code=code+'\
    if (Submodels[%d]!=null) {\n\
      lasth.Next=Submodels[%d].getHierarchy(start_level+%d+1, lasth.PathName);\n\
      while (lasth.Next!=null)\n\
        lasth=lasth.Next;\n\
    }\n' % (snum, snum, level)
	code=self.generate_hierarchy_code_rec(code, stateH[k], level+1, newpath)
    return code

  def generate_hierarchy_code(self):
    code="\
    Hierarchy h=new Hierarchy(), lasth=h;\n"
    code=self.generate_hierarchy_code_rec(code, self.eventhandler.stateH)
    code=code+"\
    return h.Next;\n"
    return code

  def generate_action_code(self):
    return ""
    code="\
    switch (code_num) {\n"
    tnum=0
    keys=self.eventhandler.trans.keys()
    keys.sort()
    for t in keys:
      for tt in t:
	tnum=tnum+1
	if tt.has_key('O'):
          print dir(tt)
          break
      break
    return code
