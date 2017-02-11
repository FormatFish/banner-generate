package inlab.AI.model;

public class Element {
	
	public String tag;
	public float scale;
	public int important;
	public int group;
	public int line;
	public int textNum;

	public Element(String tag,float scale,int important,int group,int line,int textNum) {
		// TODO Auto-generated constructor stub
		this.group = group;
		this.tag = tag;
		this.important = important;
		this.group = group;
		this.line = line;
		this.scale = scale;
		//this.textNum = textNum
	}

	public String getTag() {
		return tag;
	}

	public void setTag(String tag) {
		this.tag = tag;
	}

	public float getScale() {
		return scale;
	}

	public void setScale(float scale) {
		this.scale = scale;
	}

	public int getImportant() {
		return important;
	}

	public void setImportant(int important) {
		this.important = important;
	}

	public int getGroup() {
		return group;
	}

	public void setGroup(int group) {
		this.group = group;
	}

	public int getLine() {
		return line;
	}

	public void setLine(int line) {
		this.line = line;
	}

	public int getTextNum() {
		return textNum;
	}

	public void setTextNum(int textNum) {
		this.textNum = textNum;
	}
}
