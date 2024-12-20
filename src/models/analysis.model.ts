import { Model, DataTypes } from 'sequelize';
import { sequelize } from '../config/database';

interface AnalysisAttributes {
  id: string;
  videoId: string;
  frames: string[];
  ocrText: string[];
  features: string[];
  userFlow: string[];
}

class Analysis extends Model<AnalysisAttributes> implements AnalysisAttributes {
  public id!: string;
  public videoId!: string;
  public frames!: string[];
  public ocrText!: string[];
  public features!: string[];
  public userFlow!: string[];
}

Analysis.init(
  {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },
    videoId: {
      type: DataTypes.UUID,
      allowNull: false,
      references: {
        model: 'Videos',
        key: 'id',
      },
    },
    frames: {
      type: DataTypes.ARRAY(DataTypes.STRING),
      allowNull: false,
      defaultValue: [],
    },
    ocrText: {
      type: DataTypes.ARRAY(DataTypes.TEXT),
      allowNull: false,
      defaultValue: [],
    },
    features: {
      type: DataTypes.ARRAY(DataTypes.TEXT),
      allowNull: false,
      defaultValue: [],
    },
    userFlow: {
      type: DataTypes.ARRAY(DataTypes.TEXT),
      allowNull: false,
      defaultValue: [],
    },
  },
  {
    sequelize,
    modelName: 'Analysis',
    tableName: 'analyses',
  }
);

export default Analysis;
