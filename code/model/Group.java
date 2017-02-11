package inlab.AI.model;

import java.util.ArrayList;
import java.util.List;

public class Group {

	public int eleNum;//组内的元素数量
	
	public float scale; //图片的比例，若组内只有文字，则为0
	
	//public float quality;//跟留白空间相关，组内元素的“质量”
	
	public int important;//也是质量的衡量标准
	
	public List<Integer> index; //小组内的元素,最重要的在最前面
	
	public Group() {
		// TODO Auto-generated constructor stub
		eleNum = 0;
		//quality = 0;
		index = new ArrayList<Integer>();
		scale = 0;
	}
	
	public Group( Group group) {
		// TODO Auto-generated constructor stub
		eleNum = group.getEleNum();
		//quality = 0;
		scale = group.getScale();
		important = group.getImportant();
		index = new ArrayList<Integer>();
		
		for(int i=0;i<group.getIndex().size();i++){
			index.add(group.getIndex().get(i));
		}
		
	}
	
	public void addEleNum(int eleNum){
		this.eleNum = this.eleNum + eleNum;
	}
	
//	public void addQuality(float quality){
//		//需要修改，不是简单的相加
//		this.quality = this.quality + quality;
//	}
	
	public void addImportant(int important){
		this.important = this.important + important;
	}
	
	public void addIndex(int index){
		this.index.add(index);
	}

	
	public int getEleNum() {
		return eleNum;
	}

	public void setEleNum(int eleNum) {
		this.eleNum = eleNum;
	}

//	public float getQuality() {
//		return quality;
//	}
//
//	public void setQuality(float quality) {
//		this.quality = quality;
//	}

	public int getImportant() {
		return important;
	}

	public void setImportant(int important) {
		this.important = important;
	}

	public List<Integer> getIndex() {
		return index;
	}

	public void setIndex(List<Integer> index) {
		this.index = index;
	}

	public float getScale() {
		return scale;
	}

	public void setScale(float scale) {
		this.scale = scale;
	}
	

}
