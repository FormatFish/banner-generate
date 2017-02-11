package inlab.AI.main;

import inlab.AI.model.Element;
import inlab.AI.model.Group;
import inlab.AI.model.Relation;
import java.util.Random;

import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.List;

import javax.lang.model.util.Elements;

public class LayoutGenerate {
	
	public float layoutScale = (float) 1; //330*276的画布
	
	public float LSpace = (float) 0.4; //最低可以忍受的剩余空间
	
	public float A = 1;  //sigmoid函数的系数
	
	public float OriginImportant = 0;
	public float TotalImportant = 0;
	
	List<Relation> BestRelations = new ArrayList<Relation>();
	
	List<Relation> relations = new ArrayList<Relation>();
	
	DecimalFormat df = new DecimalFormat("#.##");
	static Random random = new Random();
 
	List<Element> elements;
	List<Group> groups;
	String relativePosition;

	public LayoutGenerate() {
		// TODO Auto-generated constructor stub
		//输入：输入元素的信息
		elements = new ArrayList<Element>();
		groups = new ArrayList<Group>();
		
		Element picture = new Element("pic", (float) (1), 10, 0, 0, 0);  //重要度越高越好,组号从0开始,重要度的获得方法，交互式的界面给用户/从深度学习中得到权重参数
		Element title = new Element("text", 0, 5, 1, 2, 4);
		Element subtitle = new Element("text", 0, 3, 1, 3, 8);
		Element describe = new Element("text", 0, 3, 2, 2, 15);
		
		//按照重要程度由高到低的放，所有后面的group的重要度顺序也是由高到低
		elements.add(picture);
		elements.add(title);
		elements.add(subtitle);
		elements.add(describe);
		
		//首先按照元素的分组进行归类，每个组有自己的"质量"，质量可以通过比例来实现
		//暂时不考虑文本元素的自动换行功能
		//每次只考虑一个关系
		int max = 0;
		for (int i=0;i< elements.size();i++){
			if ( elements.get(i).getGroup()> max )
				max = elements.get(i).getGroup();
		}

		
		for (int i=0;i <= max;i++){
			groups.add(new Group());
		}
		
		
		for (int i=0;i< elements.size();i++){
			Element element = elements.get(i);
			int groupid = element.getGroup();
			
			Group group = groups.get(groupid);
			group.addEleNum(1);
			group.addIndex(i);
			group.addImportant(element.getImportant());
			OriginImportant = OriginImportant + element.getImportant();
			//group.addQuality();
			
			if(element.tag.equals("pic")){
				group.setScale(element.getScale());
			}
		}
		
		//打印测试一下
//		for (int i=0;i<groups.size();i++){
//			List<Integer> index = groups.get(i).getIndex();
//			
//			for (int j=0;j<index.size();j++) {
//				System.out.print(index.get(j));
//			}
//			System.out.print("        "+groups.get(i).getImportant());
//			System.out.println("------");
//		}
		
		
		//布局时首先满足重要度高的
		for(int i=0;i<10;i++){
			TotalImportant = OriginImportant;
			System.out.println(groupArrange(groups,layoutScale,0,-1));
		}
			
		
		//考虑的审美指标：对称，平衡，flow----------------------不考虑对齐，留白，大小，重叠
		//再考虑平衡和对称

		  
	}
	
	public String groupArrange(List<Group> groups,  float layoutScale, int deep, int state){ //state表示上一层的位置状态，0表示左右，1表示上下，-1表示初始
		
		if(groups.size() > deep){
			
			Group group = groups.get(deep);//得到这个组元素
			
			//判断是不是最后一个
			if( groups.size() == (deep+1) ){
				TotalImportant = TotalImportant - group.getImportant();
				return elementArrange(group, layoutScale,state);
			}
			
			if (group.getScale() != 0 ){//组里面有图片，暂时没有考虑两张图片的情况
				//左右布局的概率
				float prob = layoutScale/group.getScale();      //画布比例除以图片比例，  >1则大概率的采用左右关系， <1则大概率的采用上下关系
				
				//根据这个比例调整位置概率
				if(prob > 1){
					prob =(float) ((1*1.0)/ (1+Math.pow(Math.E, -A*(prob-1))));
				}else {
					prob = -1/prob;
					prob =(float) ((1*1.0)/ (1+Math.pow(Math.E, -A*((-1/prob)-1))));
				}
				
				float positionProb =  (float)Math.random();
				
				if(positionProb <= prob){
					float ratio = group.getScale() / layoutScale;  //ratio为在左右关系时，图片在X轴上占画布的比例
					
					if( Math.random() > 0.5 )
						relativePosition = "R";
					else
						relativePosition = "L";
					
					if (ratio < LSpace || ratio > (1-LSpace)){//图片比例与画布比例差不多,按照重要度来分配空间
						ratio = group.getImportant() / TotalImportant;
						
						float deltaRandom = (float) random.nextGaussian()/5;  //产生一个均值为0，标准差为0.2，满足高斯分布的随机数
						ratio = ratio + deltaRandom * ratio;
						
						if(ratio < 0)
							ratio = 0;
						if(ratio >1)
							ratio = 1;
						
						TotalImportant = TotalImportant - group.getImportant();
						if (state == 0)
							return elementArrange(new Group(group), layoutScale * ratio,0) + "“"+df.format(ratio)+"”"+relativePosition + groupArrange(groups, (layoutScale * (1-ratio)) ,(deep+1),0);
						else 
							return "(" + elementArrange(new Group(group), layoutScale * ratio,0) + "“"+df.format(ratio)+"”"+relativePosition + groupArrange(groups, (layoutScale * (1-ratio)) ,(deep+1),0) + ")";
						
					}else {//左右排列
						//(layoutScale * (1-ratio))为下一个层级的母版
						
						float deltaRandom = (float) random.nextGaussian()/10;  //产生一个均值为0，标准差为0.1，满足高斯分布的随机数
						ratio = ratio + deltaRandom * ratio;
						
						if(ratio < 0)
							ratio = 0;
						if(ratio >1)
							ratio = 1;
						
						TotalImportant = TotalImportant - group.getImportant();
						if (state == 0)
							return elementArrange(new Group(group), layoutScale * ratio,0) + "“"+df.format(ratio)+"”"+ relativePosition + groupArrange(groups, (layoutScale * (1-ratio)) ,(deep+1),0);
						else
							return "(" + elementArrange(new Group(group), layoutScale * ratio,0) + "“"+df.format(ratio)+"”"+ relativePosition + groupArrange(groups, (layoutScale * (1-ratio)) ,(deep+1),0) + ")";
					}
					
				}else {
					float ratio =  layoutScale / group.getScale() ;  //ratio为在上下关系时，图片在Y轴上占画布的比例
					
					if( Math.random() > 0.5 )
						relativePosition = "T";
					else
						relativePosition = "B";
					
					if (ratio < LSpace || ratio > (1-LSpace)){//图片比例与画布比例差不多,按照重要度来分配空间
						ratio = group.getImportant() / TotalImportant;
						
						float deltaRandom = (float) random.nextGaussian()/5;  //产生一个均值为0，标准差为0.2，满足高斯分布的随机数
						ratio = ratio + deltaRandom * ratio;
						
						
						
						if(ratio < 0)
							ratio = 0;
						if(ratio >1)
							ratio = 1;
						
						TotalImportant = TotalImportant - group.getImportant();
						if (state == 1)
							return elementArrange(new Group(group), layoutScale / ratio,1) + "“"+df.format(ratio)+"”"+ relativePosition + groupArrange(groups, (layoutScale / (1-ratio)) ,(deep+1),1) ;
						else
							return "(" + elementArrange(new Group(group), layoutScale / ratio,1) + "“"+df.format(ratio)+"”"+ relativePosition + groupArrange(groups, (layoutScale / (1-ratio)) ,(deep+1),1) + ")";
					}else{
						
						float deltaRandom = (float) random.nextGaussian()/10;  //产生一个均值为0，标准差为0.1，满足高斯分布的随机数
						ratio = ratio + deltaRandom * ratio;

						
						if(ratio < 0)
							ratio = 0;
						if(ratio >1)
							ratio = 1;
						
						TotalImportant = TotalImportant - group.getImportant();
						if (state == 1)
							return elementArrange(new Group(group), layoutScale / ratio,1) + "“"+df.format(ratio)+"”"+ relativePosition + groupArrange(groups, (layoutScale / (1-ratio)) ,(deep+1),1);
						else
							return "(" + elementArrange(new Group(group), layoutScale / ratio,1) + "“"+df.format(ratio)+"”"+ relativePosition + groupArrange(groups, (layoutScale / (1-ratio)) ,(deep+1),1) + ")";
					}
				}
				
			}else{//不是图片
				
				float textProb;
				//根据这个比例调整位置概率
				if(layoutScale > 1){
					textProb =(float) ((1*1.0)/ (1+Math.pow(Math.E, -A*(layoutScale-1))));
				}else {
					textProb =(float) ((1*1.0)/ (1+Math.pow(Math.E, -A*((-1/layoutScale)-1))));
				}
				
				float positionProb =  (float)Math.random();
				
				if (positionProb < textProb){ //文字上下排布
					
					if( Math.random() > 0.5 )
						relativePosition = "T";
					else
						relativePosition = "B";
					
					float ratio = group.getImportant() / TotalImportant;					
					float deltaRandom = (float) random.nextGaussian()/10;  //产生一个均值为0，标准差为0.1，满足高斯分布的随机数
					ratio = ratio + deltaRandom * ratio;
					if(ratio < 0)
						ratio = 0;
					if(ratio >1)
						ratio = 1;
					
					TotalImportant = TotalImportant - group.getImportant();
					if (state == 1)
						return elementArrange(new Group(group), layoutScale / ratio,1) + "“"+df.format(ratio)+"”"+ relativePosition + groupArrange(groups, (layoutScale / (1-ratio)) ,(deep+1),1);
					else
						return "(" + elementArrange(new Group(group), layoutScale / ratio,1) + "“"+df.format(ratio)+"”"+ relativePosition + groupArrange(groups, (layoutScale / (1-ratio)) ,(deep+1),1) + ")";
				}else{ //文字左右排布
					
					if( Math.random() > 0.5 )
						relativePosition = "R";
					else
						relativePosition = "L";
					
					float ratio = group.getImportant() / TotalImportant;
					float deltaRandom = (float) random.nextGaussian()/10;  //产生一个均值为0，标准差为0.1，满足高斯分布的随机数
					ratio = ratio + deltaRandom * ratio;
					if(ratio < 0)
						ratio = 0;
					if(ratio >1)
						ratio = 1;
					
					TotalImportant = TotalImportant - group.getImportant();
					if (state == 0)
						return elementArrange(new Group(group), layoutScale * ratio,0) + "“"+df.format(ratio)+"”"+relativePosition + groupArrange(groups, (layoutScale * (1-ratio)) ,(deep+1),0);
					else 
						return "(" + elementArrange(new Group(group), layoutScale * ratio,0) + "“"+df.format(ratio)+"”"+relativePosition + groupArrange(groups, (layoutScale * (1-ratio)) ,(deep+1),0) + ")";
				}
				
			}
//			double seed  = Math.random() * 8;
//			
//			if(seed < 2){
//				return "(" + String.valueOf(deep) + "L" + groupArrange(groups,(deep+1)) + ")";
//			}else if (seed < 4){
//				return "(" + String.valueOf(deep) + "R" + groupArrange(groups,(deep+1)) + ")";
//			}else if (seed < 6){
//				return "(" + String.valueOf(deep) + "T" + groupArrange(groups,(deep+1)) + ")";
//			}else {
//				return "(" + String.valueOf(deep) + "B" + groupArrange(groups,(deep+1)) + ")";
//			}
			
		}else{
			return "";
		}
		
		
	}
	
	public String elementArrange(Group group,float layoutScale,int state){ //state表示上一层的位置状态，0表示左右，1表示上下，-1表示初始
		
		if (group.getEleNum() == 1){
			return String.valueOf(group.getIndex().get(0));
		}else{
			
			int eleIndex = group.getIndex().get(0);
			group.getIndex().remove(0);
			
			Element element = elements.get(eleIndex);
			
			
			
			if (layoutScale > 1){ //文字上下排布
				float ratio = (float) (element.getImportant()*1.0 / group.getImportant());
				
				float deltaRandom = (float) random.nextGaussian()/10;  //产生一个均值为0，标准差为0.1，满足高斯分布的随机数
				ratio = ratio + deltaRandom * ratio;
				if(ratio < 0)
					ratio = 0;
				if(ratio >1)
					ratio = 1;
				
				group.setEleNum(group.getEleNum()-1);
				group.setImportant(group.getImportant() - element.getImportant());
				if (state == 1)
					return String.valueOf(eleIndex) + "“"+df.format(ratio)+"”"+ "T" + elementArrange(group, (layoutScale / (1-ratio)),1);
				else
					return "(" + String.valueOf(eleIndex) + "“"+df.format(ratio)+"”"+ "T" + elementArrange(group, (layoutScale / (1-ratio)),1) + ")";
			}else{ //文字左右排布
				float ratio = (float) (element.getImportant()*1.0 / group.getImportant());
				
				float deltaRandom = (float) random.nextGaussian()/10;  //产生一个均值为0，标准差为0.1，满足高斯分布的随机数
				ratio = ratio + deltaRandom * ratio;
				if(ratio < 0)
					ratio = 0;
				if(ratio >1)
					ratio = 1;
				
				group.setEleNum(group.getEleNum()-1);
				group.setImportant(group.getImportant() - element.getImportant());
				if (state == 0)
					return String.valueOf(eleIndex) + "“"+df.format(ratio)+"”"+"L" + elementArrange(group, (layoutScale * (1-ratio)),0);
				else
					return "(" + String.valueOf(eleIndex) + "“"+df.format(ratio)+"”"+"L" + elementArrange(group, (layoutScale * (1-ratio)),0) + ")";
			}
		}
			
		
	}
	
	public String randomArrange(List<Group> groups, float layoutScale,int deep){ //参数为所分的组，上层框架的比例,迭代的深度（从0开始）
		
		if(groups.size() > deep){
			Group group = groups.get(deep);
			
			//判断是不是最后一个
			if( groups.size() == (deep+1) ){
				//Relation relation = new Relation(deep, 0, Relation.CENTRE, 0);
				//relations.add(relation);
				return String.valueOf(deep);
			}
			
			if (group.getScale() != 0 ){//组里面有图片
				//左右布局的概率
				float prob = layoutScale/group.getScale();      //画布比例除以图片比例，  >1则大概率的采用左右关系， <1则大概率的采用上下关系
				if(prob > 1){
					prob =(float) ((1*1.0)/ (1+Math.pow(Math.E, -A*(prob-1))));
				}else {
					prob = -1/prob;
					prob =(float) ((1*1.0)/ (1+Math.pow(Math.E, -A*(prob-1))));
				}
				
				//0-prob之间就选择左右布局，否则就选择上下布局
				float seed = (float)Math.random();
				
				if(seed <= prob){//元素左右布局
					if((int)(Math.random()+0.5) == 0){//LEFT
						
//						float ratio = group.getScale() / layoutScale;
//						
//						if (ratio < LSpace || ratio > (1-LSpace)){
//							//图片比例与画布比例差不多								
//						}
						
						
						//Relation relation = new Relation(deep, deep+1, Relation.LEFT, ratio);
						//return String.valueOf(deep) + "LEFT" + "("+ randomArrange(groups,,(deep+1)) + ")";
						
					}else{
						//RIGHT
					}
					//如何去表示和保存这个关系
					
					
				}else{//元素上下布局
					
				}

				
				//如果腾出的空间在0.3-0.5之间，可做继续的分割，否则，就3分割
				
				
				
			}else{//如果里面是文字,计算重要度
				
			}
			
			//计算审美评价值, flow,对称，平衡
			return "";
			
		}else {
			return "";
		}
		
	}
	
	
	//主函数
	public static void main(String[] args) {
		
		LayoutGenerate layoutGenerate = new LayoutGenerate();
//		while(true)
//			System.out.println( random.nextGaussian() );
	}

}
