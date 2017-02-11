package inlab.AI.model;

import java.security.PublicKey;

public class Relation {

	public final static int LEFT = 0;
	public final static int RIGHT = 1;
	public final static int TOP = 2;
	public final static int BOTTON = 3;
	public final static int CENTRE = 4;
	
	int FormerGroup; //前一个元素的id
	int LatterGroup; //后一个元素的id
	int relat;       //元素间的关系
	//元素之间关系定义
	float ratio;     //关系的比例，定义基准为画布的左边和上边
	
	public Relation(int FormerGroup, int LatterGroup, int relat,float ratio ) {
		// TODO Auto-generated constructor stub
		
		this.FormerGroup = FormerGroup;
		this.LatterGroup = LatterGroup;
		this.relat = relat;
		this.ratio = ratio;
	}


	public int getRelat() {
		return relat;
	}

	public void setRelat(int relat) {
		this.relat = relat;
	}


	public void setRatio(int ratio) {
		this.ratio = ratio;
	}


	public int getFormerGroup() {
		return FormerGroup;
	}


	public void setFormerGroup(int formerGroup) {
		FormerGroup = formerGroup;
	}


	public int getLatterGroup() {
		return LatterGroup;
	}


	public void setLatterGroup(int latterGroup) {
		LatterGroup = latterGroup;
	}


	public void setRatio(float ratio) {
		this.ratio = ratio;
	}
	
	

}
